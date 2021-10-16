import requests
from requests.auth import HTTPBasicAuth
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class UrlRequest:
    def __init__(self, logger):
        self.logger = logger

    def request_post(self, url, data, json_post = 0) :
        if json_post == 1 :
            return requests.post(url, json.dumps(data), headers={'content-type': 'application/json'}, verify=False)
        else :
            return requests.post(url, data=data, verify=False)

    def request_get(self, url) :
        return requests.get(url, verify=False)


    def request_get_content(self, url, encoding='utf-8', user=None, password=None):
        try:
            rs = requests.get(url, stream=True, verify=False)

            if rs.status_code == 401:
                rs = requests.get(url, stream=True, verify=False, auth=HTTPBasicAuth(user, password))

            if rs.status_code != 200:
                self.logger.info(f"無法取得 dpa url 內容 (status code {rs.status_code}): {url}")
                return False

            rs.encoding = rs.apparent_encoding
            if rs.encoding is None:
                rs.encoding = encoding
            try:
                content = rs.content.decode(rs.encoding)
            except:
                content = rs.content.decode('utf-8')
            content = content.replace('<![CDATA[', '').replace(']]>', '')
            rs.close()
        except Exception as e:
            print(e)
            #self.logger.info(f'url或編碼錯誤 {url}')
            content = False
        return content
