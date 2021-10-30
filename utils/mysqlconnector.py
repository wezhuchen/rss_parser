import os,json
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects.mysql import insert
from sshtunnel import SSHTunnelForwarder

class MysqlConnector:
    engine = {}
    Session = {}
    def __init__(self, service):
        if service not in MysqlConnector.engine:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            with open(os.path.join(BASE_DIR, "./conf", "db.json")) as default_config_file:
                config = json.load(default_config_file)
            if "SSH" in config["mysql"][service]:
                mysqlsql_uri = self.__ssh_forwarder(config["mysql"][service])
                print(mysqlsql_uri)
            else:
                mysqlsql_uri = self.__compose_uri(config["mysql"][service])
            engine = create_engine(mysqlsql_uri)
            MysqlConnector.engine[service] = engine
            MysqlConnector.Session[service] = sessionmaker(bind=engine)

        connection = MysqlConnector.engine[service].connect()
        self.session = MysqlConnector.Session[service](bind=connection)

    def get_session(self):
        return self.session

    def session_close(self):
        self.session.get_bind().close()
        self.session.close()   
        if 'server' in dir(self):
            self.server.stop()

    def query(self, *entities, **kwargs):
        return self.session.query(*entities, **kwargs)

    def insert(self, *entities, **kwargs):
        return self.session.insert(*entities, **kwargs)

    def execute_raw_sql(self, *entities, **kwargs):
        return self.session.execute(*entities, **kwargs)

    def __compose_uri(self, config):
        host = config["MYSQL_HOST"]
        port = config["MYSQL_PORT"]
        if port:
            host = "{}:{}".format(host, port)
        
        user = config["MYSQL_USER"]
        password = config["MYSQL_PASSWORD"]
        if password:
            user = "{}:{}".format(user, password)
        return "mysql+pymysql://{}@{}/{}??charset=utf8mb4".format(user, host, config["MYSQL_DB"])

    def __ssh_forwarder(self, config):
        self.server = SSHTunnelForwarder(
             (config["SSH"]["HOST"], config["SSH"]["PORT"]),
             ssh_password = config["SSH"]["PASSWORD"],
             ssh_username = config["SSH"]["USER"],
             remote_bind_address=(config["MYSQL_HOST"], config["MYSQL_PORT"])
        )
        #self.TUNNEL_TIMEOUT = 20.0
        self.server.start()

        host = '127.0.0.1'
        port = self.server.local_bind_port
        if port:
            host = "{}:{}".format(host, port)
        user = config["MYSQL_USER"]
        password = config["MYSQL_PASSWORD"]
        if password:
            user = "{}:{}".format(user, password)
        return "mysql+pymysql://{}@{}/{}??charset=utf8mb4".format(user, host, config["MYSQL_DB"])


class MySqlHelper:

    def __init__(self, CONN_INFO, logger=print):
        self.logger = logger
        self.sql_connector = MysqlConnector(CONN_INFO)

    def ExecuteUpdate(self, *entities, **kwargs):
        '''
            输入非查詢SQL語句
            输出：受影響的行數
        '''
        count = 0
        try:   
            result = self.sql_connector.execute_raw_sql(*entities, **kwargs)
            count = result.rowcount
        except Exception as e:
            self.logger(e)
            self.sql_connector.get_session().rollback()
        else:    
            self.sql_connector.get_session().commit()
        finally:         
            self.sql_connector.session_close()

        return count
        

    def ExecuteSelect(self, *entities, **kwargs):
        '''
            输入查詢SQL語句
            输出：查詢的結果
        '''
        result = self.sql_connector.execute_raw_sql(*entities, **kwargs)
        data = result.fetchall()       
        self.sql_connector.session_close()

        return data
        
