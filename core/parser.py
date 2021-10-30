import sys,os,traceback,logging

from utils.urlrequest import UrlRequest
from utils.logger import Logger

class ParserCore :

    def __init__(self, debug_level=logging.DEBUG) :
         self.logger = Logger(debug_level).logger

    def xml_parser(self, web_id, settings, test_mode=1) :
        settings["web_id"] = web_id
        rss_content = UrlRequest(self.logger).request_get_content(settings["rss"], 
                                                        settings.get("rss_encoding", 'utf-8'), 
                                                        settings.get("user"), 
                                                        settings.get("password")) 
        self.logger.info(rss_content)