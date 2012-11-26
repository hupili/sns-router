# -*- coding: utf-8 -*-

import sys
sys.path.append('bottle')
sys.path.append('snsapi')
import snsapi
from snsapi.snspocket import SNSPocket
from snsapi.platform import SQLite
from snsapi import utils as snsapi_utils
from snsapi.utils import json
from snsapi import snstype
from snsapi.utils import Serialize
from snsapi.snsbase import SNSBase
from snsapi.snslog import SNSLog as logger
from analysis.feature import Feature

import base64
import hashlib
import sqlite3

class SRFEQueue(SNSBase):
    """
    The queue facility of SRFE

    One thread will input messages into the Queue. 

    HTTP request handler will read messages from the Queue. 
    
    """

    SQLITE_QUEUE_CONF = {
              "url": "srfe_queue.db", 
              "channel_name": "srfe_queue", 
              "open": "yes", 
              "platform": "SQLite"
              }

    def __init__(self, snspocket = None):
        super(SRFEQueue, self).__init__(self.SQLITE_QUEUE_CONF)
        self.sp = snspocket # SNSPocket object
        #self.__mount_default_home_timeline_count()
        self.queue_conf = json.load(open('conf/queue.json', 'r'))
        self.feature_weight = self.queue_conf['feature_weight']

    #def __mount_default_home_timeline_count(self):
    #    for ch in self.sp.values():
    #        if 'home_timeline' in ch.jsonconf:
    #            ct = ch.jsonconf['home_timeline']['count']
    #            func_ht = ch.home_timeline
    #            ch.home_timeline = lambda : func_ht(count = ct)
    #            logger.debug("Set channel '%s' default ht count to %d", ch.jsonconf['channel_name'], ct)

    def _create_schema(self):
        cur = self.con.cursor()
        try:
            cur.execute("create table meta (time integer, path text)")
            cur.execute("insert into meta values (?,?)", (int(self.time()), self.jsonconf.url))
            self.con.commit()
        except sqlite3.OperationalError, e:
            if e.message == "table meta already exists":
                return 
            else:
                raise e
    
        cur.execute("""
        CREATE TABLE msg (
        id INTEGER PRIMARY KEY, 
        time INTEGER, 
        text TEXT,
        userid TEXT, 
        username TEXT, 
        mid TEXT, 
        platform TEXT, 
        digest TEXT, 
        digest_parsed TEXT, 
        digest_pyobj TEXT, 
        parsed TEXT, 
        pyobj TEXT, 
        flag TEXT, 
        weight FLOAT, 
        weight_time INTEGER
        )
        """)

        cur.execute("""
        CREATE TABLE tag (
        id INTEGER PRIMARY KEY, 
        name INTEGER 
        )
        """)

        cur.execute("""
        CREATE TABLE msg_tag (
        id INTEGER PRIMARY KEY, 
        msg_id INTEGER,  
        tag_id INTEGER
        )
        """)

        cur.execute("""
        CREATE TABLE log (
        id INTEGER PRIMARY KEY, 
        time TEXT,  
        operation TEXT
        )
        """)

        self.con.commit()

    def log(self, text):
        cur = self.con
        cur.execute("INSERT INTO log(time,operation) VALUES (?,?)", (int(self.time()), text))
        self.con.commit()
        
    def connect(self):
        '''
        Connect to SQLite3 database and create cursor. 
        Also initialize the schema if necessary. 

        '''
        url = self.jsonconf.url
        # Disable same thread checking. 
        # SQLite3 can support multi-threading. 
        # http://stackoverflow.com/questions/393554/python-sqlite3-and-concurrency
        self.con = sqlite3.connect(url, check_same_thread = False)
        self.con.isolation_level = None
        self._create_schema()

    def _pyobj2str(self, message):
        return base64.encodestring(Serialize.dumps(message))

    def _str2pyobj(self, message):
        return Serialize.loads(base64.decodestring(message))

    def _digest_pyobj(self, message):
        return hashlib.sha1(self._pyobj2str(message)).hexdigest()

    def _inqueue(self, message):
        cur = self.con.cursor()
        try:
            #Deduplicate
            #digest = self._digest_pyobj(message)
            #digest = message.digest_parsed()
            digest = message.digest()
            #logger.debug("message pyobj digest '%s'", digest)
            r = cur.execute('''
            SELECT digest FROM msg
            WHERE digest = ?
            ''', (digest, ))

            if len(list(r)) > 0:
                #logger.debug("message '%s' already exists", digest)
                return False
            else:
                logger.debug("message '%s' is new", digest)

            #TODO:
            #    This is temporary solution for object digestion. 
            #   
            #    For our Message object, the following evaluates to False!!
            #    Serialize.dumps(o) == Serialize.dumps(Serialize.loads(Serialize.dumps(o)))
            #
            #    To perform deduplication and further refer to this message, 
            #    we store the calculated digestion as an attribute of the message. 
            #    Note however, after this operation the digest of 'message' will not 
            #    be the valued stored therein! This is common problem in such mechanism, 
            #    e.g. UDP checksum. Developers should have this in mind. 
            message.digest_pyobj = self._digest_pyobj(message)

            cur.execute('''
            INSERT INTO msg(
            time , 
            text ,
            userid , 
            username , 
            mid , 
            platform , 
            digest , 
            digest_parsed , 
            digest_pyobj , 
            parsed , 
            pyobj , 
            flag 
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (\
                    message.parsed.time,\
                    message.parsed.text,\
                    message.parsed.userid,\
                    message.parsed.username,\
                    str(message.ID),\
                    message.platform,\
                    message.digest(),\
                    message.digest_parsed(),\
                    #self._digest_pyobj(message),\
                    message.digest_pyobj,\
                    message.dump_parsed(),\
                    self._pyobj2str(message),\
                    "unseen"
                    ))
            return True
        except Exception, e:
            logger.warning("failed: %s", str(e))
            #print message
            #raise e
            return False

    def _home_timeline(self, channel):
        ch = self.sp[channel]
        if 'home_timeline' in ch.jsonconf:
            ct = ch.jsonconf['home_timeline']['count']
        else:
            ct = 20
        return ch.home_timeline(ct)

    def input(self, channel = None):
        if channel:
            ml = self._home_timeline(channel)
        else:
            ml = snstype.MessageList()
            for chn in self.sp:
                ml.extend(self._home_timeline(chn))

        count = 0 
        for m in ml:
            if self._inqueue(m):
                count += 1
        logger.info("Input %d new message", count)
        self.log("Input %d new message" % count)

    def get_unseen_count(self):
        cur = self.con.cursor()
        
        r = cur.execute('''
        SELECT count(*) FROM msg  
        WHERE flag='unseen'
        ''')
        
        try:
            return r.next()[0]
        except Exception, e:
            logger.warning("Catch Exception: %s", e)
            return -1

    def output(self, count = 20):
        cur = self.con.cursor()
        
        r = cur.execute('''
        SELECT id,time,userid,username,text,pyobj FROM msg  
        WHERE flag='unseen'
        ORDER BY time DESC LIMIT ?
        ''', (count,))

        message_list = snstype.MessageList()
        for m in r:
            obj = self._str2pyobj(m[5])
            obj.msg_id = m[0]
            message_list.append(obj)
        #for m in r:
        #    message_list.append(self.Message({
        #            'time':m[0],
        #            'userid':m[1],
        #            'username':m[2],
        #            'text':m[3]
        #            },\
        #            platform = self.jsonconf['platform'],\
        #            channel = self.jsonconf['channel_name']\
        #            ))

        return message_list

    def sql(self, condition):
        cur = self.con.cursor()
        
        try:
            # We trust the client string. This software is intended for personal use. 
            qs = "SELECT id,pyobj FROM msg WHERE %s" % condition
            r = cur.execute(qs)
            logger.debug("SQL query string: %s", qs)

            message_list = snstype.MessageList()
            for m in r:
                obj = self._str2pyobj(m[1])
                obj.msg_id = m[0]
                message_list.append(obj)
            return message_list
        except Exception, e:
            logger.warning("Catch exception when executing '%s': %s", condition, e)
            return snstype.MessageList()

    def raw(self, msg_id):
        cur = self.con.cursor()
        
        r = cur.execute('''
        SELECT pyobj FROM msg  
        WHERE id=?
        ''', (msg_id,))

        return self._str2pyobj(list(r)[0][0]).raw

    def flag(self, message, fl):
        '''
        flag v.s. message: 1 <-> 1

        '''
        if isinstance(message, snstype.Message):
            #digest = message.digest_pyobj
            msg_id = message.msg_id
        else:
            msg_id = message

        cur = self.con.cursor()

        ret = False
        try:
            cur.execute('''
            UPDATE msg
            SET flag=?
            WHERE id=?
            ''', (fl, msg_id))
            self.con.commit()
            ret = True
        except Exception, e:
            logger.warning("Catch exception: %s", e)

        self.log("[flag]%s;%s;%s" % (msg_id, fl, ret))
        return ret

    def get_tags(self):
        if not hasattr(self, '_tags'):
            self._tags = {}
            cur = self.con.cursor()
            r = cur.execute('''
            SELECT id,name FROM tag  
            ''')
            for t in cur:
                self._tags[t[0]] = t[1]
        return self._tags

    def tag(self, message, tg):
        '''
        flag v.s. message: * <-> *

        '''
        if isinstance(message, snstype.Message):
            msg_id = message.msg_id
        else:
            msg_id = message

        cur = self.con.cursor()

        ret = False
        try:
            cur.execute('''
            INSERT INTO msg_tag(msg_id, tag_id)
            VALUES (?,?)
            ''', (msg_id, tg))
            self.con.commit()
            ret = True
        except Exception, e:
            logger.warning("Catch exception: %s", e)

        self.log("[tag]%s;%s;%s" % (msg_id, tg, ret))
        return ret

    def forward(self, msg_id, comment):
        cur = self.con.cursor()
        try:
            r = cur.execute('''
            SELECT pyobj FROM msg
            WHERE id=?
            ''', (msg_id, ))
            str_obj = r.next()[0]
            message = self._str2pyobj(str_obj)

            result = self.sp.forward(message, comment)

            self.log('[forward]%s;%s;%s' % (msg_id, result, comment)) 
            return result
        except Exception, e:
            logger.warning("Catch exception: %s", e)
            return {}

    def _weight_feature(self, msg):
        score = 0.0
        for (f, w) in self.feature_weight.items():
            if f in msg.feature:
                score += msg.feature[f] * w
        return score

    def reweight(self, msg_id):
        cur = self.con.cursor()
        try:
            r = cur.execute('''
            SELECT pyobj FROM msg
            WHERE id=?
            ''', (msg_id,))
            m = self._str2pyobj(list(r)[0][0])
            Feature.extract(m)
            w = self._weight_feature(m)
            t = int(self.time())
            r = cur.execute('''
            UPDATE msg
            SET weight=?,weight_time=?
            WHERE id=?
            ''', (w, t, msg_id))
        except Exception, e:
            logger.warning("Catch exception: %s", e)

    def reweight_all(self, last_update_time = None):
        begin = self.time()
        cur = self.con.cursor()
        try:
            if last_update_time is None:
                r = cur.execute('''
                SELECT id from msg
                ''')
            else:
                r = cur.execute('''
                SELECT id from msg
                WHERE weight_time is NULL or weight_time < ?
                ''', (last_update_time, ))
            for m in r:
                self.reweight(m[0])
        except Exception, e:
            logger.warning("Catch exception: %s", e)
        end = self.time()
        logger.info("Reweight done. Time elapsed: %.2f", end - begin)

if __name__ == '__main__':
    sp = SNSPocket()
    sp.load_config()
    sp.auth()

    q = SRFEQueue(sp)
    q.connect()
    #q.input()

    #print sp.home_timeline()


#    def _update_text(self, text):
#        m = self.Message({\
#                'time':int(self.time()),
#                'userid':self.jsonconf['userid'],
#                'username':self.jsonconf['username'],
#                'text':text
#                }, \
#                platform = self.jsonconf['platform'],\
#                channel = self.jsonconf['channel_name']\
#                )
#        return self._update_message(m)
#
#    def _update_message(self, message):
#
#    def update(self, text):
#        if isinstance(text, str):
#            return self._update_text(text)
#        elif isinstance(text, unicode):
#            return self._update_text(text)
#        elif isinstance(text, snstype.Message):
#            return self._update_message(text)
#        else:
#            logger.warning('unknown type: %s', type(text))
#            return False
