import sys,os,traceback,logging
from bs4 import BeautifulSoup
from dateutil.parser import parse
import urllib
import re
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
        item_dict['image'] = "_"
        if settings['have_image_tag'] !="":
            item_dict['image'] = item.find('img').get('src', '_') 


        item_dict["web_id"] = web_id

        return self.transofrm_data(item_dict, settings) 

    def transofrm_data(self, item_dict, settings):
        item_dict["title"] = self.text_cleaning(item_dict["title"])
        item_dict["description"] = self.text_cleaning(item_dict["description"])

        if not item_dict["link"]:
            print(f'web id: {item_dict["web_id"]}, url: {str(item_dict["link"])}, 連結失效')
            return False

        item_dict["link"] = self.remove_utm_parameter(item_dict["link"], settings.get("utm_param", {}))

        if item_dict['image'] != "_": 
            item_dict['image'] = 'https://' + item_dict['image'].split(sep='//', maxsplit=1)[1]

        item_dict['pubDate'] = parse(item_dict['pubDate']).strftime("%Y-%m-%d %H:%M:%S")

        item_dict['keywords'] = item_dict.get('keywords', '')
        item_dict['category'] = item_dict.get('category', '')
        
        if item_dict['keywords'] in ['no_keyword']:
            item_dict['keywords'] = ''

        return item_dict

    def remove_utm_parameter(self, url, utm_param={}):
        parsed_url = urllib.parse.urlparse(url)
        parsed_query = urllib.parse.parse_qs(parsed_url.query)

        for utm_key in ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content','avivid_uuid','push_date','access', 'fbclid']:
            if utm_key in parsed_query:
                del parsed_query[utm_key]
        parsed_query.update(utm_param)
        new_parsed_url = parsed_url._replace(query="&".join([key+"="+parsed_query[key][0] for key in parsed_query]))
        url = urllib.parse.urlunparse(new_parsed_url)
        return url

    def remove_urls(self, text):
        text = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', text, flags=re.MULTILINE)
        text = re.sub(r'^[a-zA-z]+://(\w+(-\w+)*)(\.(\w+(-\w+)*))*(\?\S*)?$', '', text)
        return(text)

    # 去除原始字符串中空格
    def remove_space(self, text):
        text = text.strip().replace('&nbsp;',' ')#remove space
        text = re.sub(r'\s+', ' ', text)  # trans 多空格 to空格
        text = re.sub(r'\n+', ' ', text)  # trans 换行 to空格
        text = re.sub(r'\t+', ' ', text)  # trans Tab to空格
        text = text.strip()
        return text

    def text_cleaning(self, text):
        html_tag = re.compile(r"<\s*(\S+)(\s[^>]*)?>(.*?)<\s*\/\1\s*>")
        text = self.remove_urls(text)
        text = html_tag.sub(" ", text )
        text = self.remove_space(text)

        return text
