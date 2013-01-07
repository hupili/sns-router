# -*- coding: utf-8 -*-

# Previous import here for possible future use
# import sys
# sys.path.append('../bottle')
# from snsapi.snspocket import SNSPocket
# from snsapi.platform import SQLite
# from snsapi import utils as snsapi_utils
# from snsapi.snsbase import SNSBase
# 
# import base64
# import hashlib
# import sqlite3

import sys
sys.path.append('../snsapi')
#sys.path.append('ranking/feature_plugin')
import snsapi
from snsapi import snstype
from snsapi.snslog import SNSLog as logger
from snsapi.utils import json
from snsapi.utils import Serialize
import re
import random

from urlext import url_extract
from userext import user_extract

class Feature(object):
    """docstring for Feature"""

    env = {
            "dir_conf": "./conf",
            "dir_kdb": "./kdb",
            }

    feature_extractors = []

    try:
        awjson = json.loads(open('conf/autoweight.json').read())
        features = awjson['features'] 
        import plugin
        for f in features:
            module_name = f[0]
            class_name = f[1]
            #print module_name
            #print class_name
            mo = __import__("ranking.plugin.%s" % module_name, fromlist=["ranking.plugin"])
            cl = getattr(mo, class_name)
            feature_extractors.append(cl(env))
            #TODO:
            #    Make the dynamic import method better (more standard ways).
            #    The current import method is borrowed from:
            #        http://stackoverflow.com/questions/301134/dynamic-module-import-in-python
            #    It just works. 
            #cl = __import__("plugin.%s.%s" % (module_name, class_name), fromlist=["plugin.%s" % module_name])
            #cl = getattr(getattr(plugin, module_name), class_name)
    except IOError:
        logger.warning('No "conf/autoweight.json"!')
    except KeyError:
        logger.warning('No "features" defined"!')

    def __init__(self):
        super(Feature, self).__init__()
        
    @staticmethod
    def extract(msg):
        '''
        Feature extraction. 
        It will extract features to a dict and store in "msg.feature". 

        msg: an snstype.Message object

        '''
        if not isinstance(msg, snstype.Message): 
            logger.warning("Cannot extract feature for non snstype.Message object")
            return 
        
        # Add all kinds of features
        msg.feature = {}

        for fe in Feature.feature_extractors:
            fe.add_features(msg)

