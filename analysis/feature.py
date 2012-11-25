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
    def extract(msg):
        '''
        Feature extraction. 
        It will extract features to a dict and store in "msg.feature". 

        msg: an snstype.Message object

        '''
        if not isinstance(msg, snstype.Message): 
            logger.warning("Cannot extract feature for non snstype.Message object")
            return 
        
        feature = {}

        # Add all kinds of features
        feature['text_len'] = len(msg.parsed.text)
        if 'text_orig' in msg.parsed:
            feature['text_orig_len'] = len(msg.parsed.text_orig)
        else:
            feature['text_orig_len'] = 0

        r = re.compile(r'https?://')
        if r.search(msg.parsed.text):
            feature['contain_link'] = 1
        else:
            feature['contain_link'] = 0 

        msg.feature = feature

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
