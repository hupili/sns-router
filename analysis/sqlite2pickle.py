# -*- coding: utf-8 -*-

# Dump sqlite3 data to python pickle
# About:
# 1.5G, 1 minute

import sys
sys.path.append('../bottle')
sys.path.append('../snsapi')
import snsapi
from snsapi.snspocket import SNSPocket
from snsapi.platform import SQLite
from snsapi import utils as snsapi_utils
from snsapi import snstype
from snsapi.utils import Serialize
from snsapi.snsbase import SNSBase
from snsapi.snslog import SNSLog as logger

import base64
import hashlib
import sqlite3

class SQLite2Pickle(object):
    """docstring for SQLite2Pickle"""
    def __init__(self):
        super(SQLite2Pickle, self).__init__()
        self.jsonconf = snsapi_utils.JsonDict()
        
    def load(self, fn_sqlite):
        '''
        Connect to SQLite3 database and create cursor. 
        Also initialize the schema if necessary. 

        '''
        url = fn_sqlite
        # Disable same thread checking. 
        # SQLite3 can support multi-threading. 
        # http://stackoverflow.com/questions/393554/python-sqlite3-and-concurrency
        self.con = sqlite3.connect(url, check_same_thread = False)
        self.con.isolation_level = None

    def _str2pyobj(self, message):
        return Serialize.loads(base64.decodestring(message))

    def dump(self, fn_pickle):
        cur = self.con.cursor()
        
        r = cur.execute('''
        SELECT id,time,userid,username,text,pyobj,flag FROM msg  
        ''')
        message_list = snstype.MessageList()
        for m in r:
            obj = self._str2pyobj(m[5])
            obj.msg_id = m[0]
            obj.flag = m[6]
            message_list.append(obj)

        r = cur.execute('''
        SELECT msg_id,tag_id FROM msg_tag
        ''')
        tag_list = []
        for m in r:
            tag_list.append(m)

        message = {
                'message_list': message_list, 
                'tag_list': tag_list
                }

        with open(fn_pickle, 'w') as fp:
            fp.write(Serialize.dumps(message))

if __name__ == '__main__':
    s2p = SQLite2Pickle()
    s2p.load('srfe.db')
    s2p.dump('message.pickle')
    
