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
import cPickle as Serialize
import snsapi
from snsapi import snstype
from snsapi.snslog import SNSLog as logger
from snsapi.utils import json
from wordseg import wordseg_clean
import re
import random

from urlext import url_extract
from userext import user_extract

class FeatureBase(object):
    """
    Base class for features
    
    """
    def __init__(self, env):
        '''
        env: Environment variables

        '''
        super(FeatureBase, self).__init__()
        self.env = env
        # If one want the feature able to export into Weka's arff format, 
        # the schema field is essential. It is a valid arff attribute 
        # definition string, e.g.: (only inside quotes)
        #    * "numeric"
        #    * "{no, yes}"
        # To enable auto training by 'autoweight.py' script, features are 
        # required to be "numeric". However, there may be some use cases 
        # for nominal values which is represented in numeric form. e.g. the
        # 'contain_link' feature takes either 0 or 1. As long as the appearance
        # is "0" or "1", our script can process it. If you want to incorporate
        # more information into arff exports, you can use "{0, 1}", insead of
        # "numeric". We'll set the default to be "numeric".
        self.schema = {"feature": "numeric"}

    def add_features(self, msg):
        '''
        Add features to msg object. 

        msg: snsapi.snstype.Message object

        '''
        msg.feature['feature'] = 1.0

class FeatureEcho(FeatureBase):
    def __init__(self, env):
        super(FeatureEcho, self).__init__(env)

        fn_channel = self.env['dir_conf'] + '/channel.json'
        self.schema = {"echo": "numeric"}

        self.username = []
        fields = ["user_name", "username", "address"]    
        with open(fn_channel) as fp:
            for ch in json.loads(fp.read()):
                for f in fields:
                    if f in ch:
                        self.username.append(ch[f])

    def add_features(self, msg):
        for un in self.username:
            if msg.parsed['username'].count(un):
                msg.feature['echo'] = 1.0
                return
        msg.feature['echo'] = 0.0
        return

class FeatureTopic(FeatureBase):
    """docstring for FeatureTopic"""
    def __init__(self, env):
        super(FeatureTopic, self).__init__(env)
        self.schema = {
                "topic_tech": "numeric",
                "topic_news": "numeric",
                "topic_interesting": "numeric",
                "topic_nonsense": "numeric",
                }

        # Topic dict
        fn_tdict = self.env['dir_kdb'] + "/tdict.pickle"
        self.tdict = Serialize.loads(open(fn_tdict).read())

    def _topic(self, dct, msg):
        score = 0.0
        terms = wordseg_clean(msg.parsed.text)
        for t in terms:
            if t.text in dct:
                score += dct[t.text]
        return score

    def add_features(self, msg):
        msg.feature['topic_tech'] = self._topic(self.tdict['tech'], msg)
        msg.feature['topic_news'] = self._topic(self.tdict['news'], msg)
        msg.feature['topic_interesting'] = self._topic(self.tdict['interesting'], msg)
        msg.feature['topic_nonsense'] = self._topic(self.tdict['nonsense'], msg)
        
        msg.feature['topic_interesting'] /= 0.08772
        msg.feature['topic_nonsense'] /= 0.25152
        msg.feature['topic_tech'] /= 0.04399
        msg.feature['topic_news'] /= 0.37376

class FeatureUser(FeatureBase):
    """docstring for FeatureTopic"""
    def __init__(self, env):
        super(FeatureUser, self).__init__(env)
        self.schema = {
                "user_tech": "numeric",
                "user_news": "numeric",
                "user_interesting": "numeric",
                "user_nonsense": "numeric",
                }

        # User dict
        fn_udict = self.env['dir_kdb'] + "/udict.pickle"
        self.udict = Serialize.loads(open(fn_udict).read())

    def _user(self, dct, msg):
        if msg.parsed.username in dct:
            return dct[msg.parsed.username]
        else:
            return 0

    def add_features(self, msg):
        msg.feature['user_tech'] = self._user(self.udict['tech'], msg)
        msg.feature['user_news'] = self._user(self.udict['news'], msg)
        msg.feature['user_interesting'] = self._user(self.udict['interesting'], msg)
        msg.feature['user_nonsense'] = self._user(self.udict['nonsense'], msg)

class FeatureFace(FeatureBase):
    """docstring for FeatureBase"""
    def __init__(self, env):
        super(FeatureFace, self).__init__(env)
        self.schema = {
                "test": "numeric",
                }

    def add_features(self, msg):
        msg.feature['test'] = 1

class FeatureNoise(FeatureBase):
    """docstring for FeatureNoise"""
    def __init__(self, env):
        super(FeatureNoise, self).__init__(env)
        self.schema = {
                "noise": "numeric"
                }

    def add_features(self, msg):
        msg.feature['noise'] = random.random()

class FeatureLink(FeatureBase):
    """docstring for FeatureLink"""
    def __init__(self, env):
        super(FeatureLink, self).__init__(env)
        self.schema = {
                "contain_link": "{0,1}"
                }
        
    def add_features(self, msg):
        r = re.compile(r'https?://')
        if r.search(msg.parsed.text):
            msg.feature['contain_link'] = 1
        else:
            msg.feature['contain_link'] = 0 

class Feature(object):
    """docstring for Feature"""

    env = {
            "dir_conf": "./conf",
            "dir_kdb": "./kdb",
            }

    feature_extractors = []
    from feature_plugin.length import FeatureLength
    feature_extractors.append(FeatureLength(env))
    feature_extractors.append(FeatureLink(env))
    feature_extractors.append(FeatureFace(env))
    feature_extractors.append(FeatureTopic(env))
    feature_extractors.append(FeatureUser(env))
    feature_extractors.append(FeatureEcho(env))
    feature_extractors.append(FeatureNoise(env))

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

def extract_all():
    import time
    begin = time.time()
    message = Serialize.loads(open('workspace.pickle').read())
    end = time.time()
    print "Load finish. Time elapsed: %.3f" % (end - begin)

    begin = time.time()
    for m in message['message_list']:
        Feature.extract(m)
    end = time.time()
    print "Feature extraction finish. Time elapsed: %.3f" % (end - begin)

    begin = time.time()
    open('workspace.pickle', 'w').write(Serialize.dumps(message))
    end = time.time()
    print "Dump finish. Time elapsed: %.3f" % (end - begin)

def get_test_case():
    message = Serialize.loads(open('workspace.pickle').read())
    # The following list mean nothing without concrete data. 
    # If you want to use my feature extraction module, please 
    # construct your own test case list. 
    case_id_list = [
            2, #length, http link
            1116, #test face icon (Tencent)
            3897, #topic tech
            9535, #topic tech
            18202, #topic tech
            15700, #topic news
            22076, #topic news
            23106, #topic news
            13401, #interesting
            3838, #topic nonsense
            834, #topic nonsense
            21182, #topic nonsense
            5414, #topic nonsense
            63, #renren long message
            32505, #echo 
            5027, #remove face
            ]
    case = []
    for cid in case_id_list:
        case.append(message['dict_msg'][cid])
    open('case.pickle', 'w').write(Serialize.dumps(case))

def run_test_case():
    message_list = Serialize.loads(open('case.pickle').read())
    for m in message_list:
        Feature.extract(m)
        print "===="
        print m
        print "----"
        #print m.feature
        for f in sorted([f for f in m.feature]):
            print "%s: %.5f" % (f, m.feature[f])
        print "===="

if __name__ == '__main__':
    try:
        run_test_case()
    except Exception, e:
        print e
