# -*- coding: utf-8 -*-
#
# Select samples from 'workspace.pickle' to train weights automatically. 
#

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

import base64
import hashlib
import sqlite3
import random

# Number of 'null' labeled messages to extract
NULL_SAMPLES = 800

if __name__ == '__main__':
    import time
    begin = time.time()
    message = Serialize.loads(open('workspace.pickle').read())
    end = time.time()
    print "Load finish. Time elapsed: %.3f" % (end - begin)

    print "Start to extract samples"

    candidates = []
    null_msg = []

    for m in message['seen_list']:
        if len(m.tags) >= 1:
            candidates.append(m)
        else:
            null_msg.append(m)

    prob = float(NULL_SAMPLES) / (len(message['seen_list']) - len(candidates))
    if prob > 1.0:
        prob = 1.0
    print "Selecting null message probability: %.3f" % (prob)

    for m in null_msg:
        if random.random() < prob:
            m.tags = {"null": 1}
            candidates.append(m)

    print "Total %d samples extracted" % (len(candidates))

    open('samples.pickle', 'w').write(Serialize.dumps(candidates))
