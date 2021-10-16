import sys,os,inspect,traceback
import json,collections,datetime,time
from importlib.machinery import SourceFileLoader 
os_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os_path + '/conf/')
sys.path.append(os_path + '/core/')
sys.path.append(os_path + '/utils/')
from importlib.machinery import SourceFileLoader 
from utils.jsonloader import Jsonloader


config_path = os_path + "/conf/"
try :
    config = Jsonloader(config_path + "default.json").getJsonDataMapping()
    cron_enabled = int(config[config["env"]]["cron_enabled"])
    if cron_enabled == 1 :
        settings = Jsonloader(config_path + "settings.json").getJsonDataMapping()
        for web_id, setup in settings.items():
            if int(setup["enabled"]) == 0 :
                continue
            core_parser = os.path.join(os_path, "core", "parser.py")
            class_loader = SourceFileLoader(setup["class_name"], core_parser).load_module()
            class_instance = getattr(class_loader,setup["class_name"])()
            getattr(class_instance, setup["exec_method_name"])(web_id, setup, setup['test_mode']) 

except :
    print (traceback.format_exc())