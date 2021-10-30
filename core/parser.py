import sys,os,traceback,logging
from bs4 import BeautifulSoup

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
        if not rss_content :
            self.logger.info( f'Error web id: {web_id}' )
            return 3011
        
        item_format = settings.get("item_format", "item")

        tags = BeautifulSoup(rss_content, 'xml').find_all(item_format)
        if len(tags)==0:
            self.logger.info( f'Error web id: {web_id} BeautifulSoup 解析有錯')
            return 3030

        items = []
        for item in tags:
            items.append(self.map_rss_tag_xml(item, settings["options"], web_id))
        self.logger.info(items)

    def map_rss_tag_xml(self, item, settings, web_id):

        item_dict = {}
        for k ,v in settings["db_mapping"].items() :
            try:
                item_dict[k] = item.find(v).getText().strip()
            except:
                item_dict[k] = ""
        if settings['have_image_tag'] == 0:
            try:
                item_dict['image'] = item.find('img').get('src', '_') 
            except:
                item_dict['image'] = "_"

        item_dict["web_id"] = web_id

        return item_dict