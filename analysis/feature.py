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
import cPickle as Serialize
import snsapi
from snsapi import snstype
from snsapi.snslog import SNSLog as logger
import re

class Feature(object):
    """docstring for Feature"""
    def __init__(self):
        super(Feature, self).__init__()

    @staticmethod
    def face(msg):
        msg.feature['test'] = 1

    @staticmethod
    def length(msg):
        msg.feature['text_len'] = len(msg.parsed.text)

        if 'text_orig' in msg.parsed:
            msg.feature['text_orig_len'] = len(msg.parsed.text_orig)
        else:
            msg.feature['text_orig_len'] = 0

    @staticmethod
    def link(msg):
        r = re.compile(r'https?://')
        if r.search(msg.parsed.text):
            msg.feature['contain_link'] = 1
        else:
            msg.feature['contain_link'] = 0 
        
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
        Feature.length(msg)
        Feature.link(msg)
        Feature.face(msg)

        #msg.feature = feature

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
    case_id_list = [
            2, #length, http link
            1116, #test face icon (Tencent)
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
        print m.feature
        print "===="

if __name__ == '__main__':
    run_test_case()
