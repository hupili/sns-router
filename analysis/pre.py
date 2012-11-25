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

    # load
    begin = time.time()
    message = Serialize.loads(open('message.pickle').read())
    end = time.time()
    print "Load finish. Time elapsed: %.3f" % (end - begin)

    # Preprocessing
    tl = message['tag_list']
    td = {}
    td_r = {}
    for (msg_id, tag_id) in tl:
        #print "msg_id: %d, tag_id: %d" % (msg_id, tag_id)
        if not msg_id in td:
            td[msg_id] = {}
        td[msg_id][tag_id] = 1
        if not tag_id in td_r:
            td_r[tag_id] = {}
        td_r[tag_id][msg_id] = 1
    #tl_r = [(t(2), t(1)) for t in tl]
    #dl = dict(tl)
    #dl_r = dict(tl_r)
    message['dict_msg2tag'] = td
    message['dict_tag2msg'] = td_r

    ml = message['message_list']
    md = {}
    for m in ml:
        if m.msg_id in td:
            m.tags = td[m.msg_id]
        else:
            m.tags = {}
        md[m.msg_id] = m
    message['dict_msg'] = md 

    # save 
    begin = time.time()
    open('workspace.pickle', 'w').write(Serialize.dumps(message))
    end = time.time()
    print "Save finish. Time elapsed: %.3f" % (end - begin)
