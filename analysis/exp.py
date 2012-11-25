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

import base64
import hashlib
import sqlite3

if __name__ == '__main__':
    import time
    begin = time.time()
    message = Serialize.loads(open('workspace.pickle').read())
    end = time.time()
    print "Load finish. Time elapsed: %.3f" % (end - begin)
