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

    # tag2msg and msg2tag dict
    tl = message['tag_list']
    td = {}
    td_r = {}
    for (msg_id, tag_id) in tl:
        if not msg_id in td:
            td[msg_id] = {}
        td[msg_id][tag_id] = 1
        if not tag_id in td_r:
            td_r[tag_id] = {}
        td_r[tag_id][msg_id] = 1
    message['dict_msg2tag'] = td
    message['dict_tag2msg'] = td_r

    # 1. add tags attributes to msg
    # 2. make msg dict
    # 3. make seen list
    ml = message['message_list']
    md = {}
    seen_list = []
    for m in ml:
        if m.flag == "seen":
            seen_list.append(m)
        if m.msg_id in td:
            m.tags = td[m.msg_id]
        else:
            m.tags = {}
        md[m.msg_id] = m
    message['dict_msg'] = md 
    message['seen_list'] = seen_list

    # save 
    begin = time.time()
    open('workspace.pickle', 'w').write(Serialize.dumps(message))
    end = time.time()
    print "Save finish. Time elapsed: %.3f" % (end - begin)
