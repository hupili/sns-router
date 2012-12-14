# -*- coding: utf-8 -*-

import sys
sys.path.append('snsapi')
import cPickle as Serialize
import snsapi
#from snsapi import snstype
#from snsapi.snslog import SNSLog as logger
#from snsapi.utils import json
#from wordseg import wordseg_clean
#import re
#import random
#from urlext import url_extract
#from userext import user_extract

from ranking.feature import Feature

def extract_all():
    import time
    begin = time.time()
    message = Serialize.loads(open('analysis/workspace.pickle').read())
    end = time.time()
    print "Load finish. Time elapsed: %.3f" % (end - begin)

    begin = time.time()
    for m in message['message_list']:
        Feature.extract(m)
    end = time.time()
    print "Feature extraction finish. Time elapsed: %.3f" % (end - begin)

    begin = time.time()
    open('analysis/workspace.pickle', 'w').write(Serialize.dumps(message))
    end = time.time()
    print "Dump finish. Time elapsed: %.3f" % (end - begin)

def get_test_case():
    message = Serialize.loads(open('analysis/workspace.pickle').read())
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
    message_list = Serialize.loads(open('analysis/case.pickle').read())
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
