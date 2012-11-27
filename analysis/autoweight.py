# -*- coding: utf-8 -*-

import sys
sys.path.append('../bottle')
sys.path.append('../snsapi')
import snsapi
from snsapi.snspocket import SNSPocket
from snsapi.platform import SQLite
from snsapi import utils as snsapi_utils
from snsapi import snstype
# On my server, pickle uses 24s to load 
# cPickle uses 6s to load. 
# very significant
#from snsapi.utils import Serialize
import cPickle as Serialize
from snsapi.snsbase import SNSBase
from snsapi.snslog import SNSLog as logger

from feature import Feature

import base64
import hashlib
import sqlite3

class AutoWeight(object):
    """docstring for AutoWeight"""
    def __init__(self):
        super(AutoWeight, self).__init__()
        
    feature_weight = {
    "contain_link": 1.00000, 
    "test": 1.00000, 
    "text_len": 0, 
    "text_orig_len": 0.01, 
    "topic_interesting": 30, 
    "topic_news": 30, 
    "topic_nonsense": -100, 
    "topic_tech": 500
    }

    def _weight_feature(self, msg):
        Feature.extract(msg)
        score = 0.0
        for (f, w) in self.feature_weight.items():
            if f in msg.feature:
                score += msg.feature[f] * w
        return score

if __name__ == '__main__':
    import time
    begin = time.time()
    samples = Serialize.loads(open('samples.pickle').read())
    end = time.time()
    print "Load finish. Time elapsed: %.3f" % (end - begin)

    aw = AutoWeight()
    ranked = sorted(samples, key = lambda m: aw._weight_feature(m), reverse = True)
    open('ranking.pickle', 'w').write(Serialize.dumps(ranked))
