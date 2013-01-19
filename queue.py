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

        try:
            self.queue_conf = json.loads(open('conf/queue.json', 'r').read())
        except IOError, e:
            logger.warning("No conf/queue.json, use defaults")
            self.queue_conf = {}

        if 'ranking' in self.queue_conf and self.queue_conf['ranking'] == "yes":
            from ranking import score
            from ranking import feature
            self.score = score.Score()
            self.Feature = feature.Feature
        else:
            self.score = None
            self._weight_feature = lambda m: 0

    def reload_config(self, conf = None):
        self.score.load_weight()

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
        name INTEGER, 
        visible INTEGER,
        parent INTEGER
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
            # Deduplicate
            # Explain the problem of the following two methods for future reference:
            # 1. digest = self._digest_pyobj(message)
            #    Python object are hashed to different values even the SNS message 
            #    fields are all the same. 
            # 2. digest = message.digest_parsed()
            #    I forget what is the problem.. I should have noted before. 
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
            flag , 
            weight ,
            weight_time
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
                    "unseen", 
                    self._weight_feature(message),
                    int(self.time())
                    ))
            return True
        except Exception, e:
            logger.warning("failed: %s", str(e))
            #print message
            #raise e
            return False

    def _home_timeline(self, channel):
        return self.sp.home_timeline(channel=channel)
        #ch = self.sp[channel]
        # The following logic is moved into SNSAPI
        #if 'home_timeline' in ch.jsonconf:
        #    ct = ch.jsonconf['home_timeline']['count']
        #else:
        #    ct = 20
        #return ch.home_timeline(ct)

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
        SELECT id,time,userid,username,text,pyobj,weight FROM msg  
        WHERE flag='unseen'
        ORDER BY time DESC LIMIT ?
        ''', (count,))

        message_list = snstype.MessageList()
        for m in r:
            obj = self._str2pyobj(m[5])
            obj.msg_id = m[0]
            obj.weight = m[6]
            message_list.append(obj)

        return message_list

    def output_ranked(self, count, younger_than):
        latest_time = int(self.time() - younger_than)
        cur = self.con.cursor()
        
        r = cur.execute('''
        SELECT id,time,userid,username,text,pyobj,weight FROM msg  
        WHERE flag='unseen' AND time>?
        ORDER BY weight DESC LIMIT ?
        ''', (latest_time, count))

        message_list = snstype.MessageList()
        for m in r:
            obj = self._str2pyobj(m[5])
            obj.msg_id = m[0]
            obj.weight = m[6]
            message_list.append(obj)

        return message_list

    def sql(self, condition):
        cur = self.con.cursor()
        
        try:
            # We trust the client string. This software is intended for personal use. 
            qs = "SELECT DISTINCT msg.id,msg.pyobj FROM msg,msg_tag WHERE %s" % condition
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

    def why(self, msg_id):
        cur = self.con.cursor()
        
        r = cur.execute('''
        SELECT pyobj FROM msg  
        WHERE id=?
        ''', (msg_id,))

        m = self._str2pyobj(list(r)[0][0])
        self.Feature.extract(m)
        
        ret = {
                "feature": m.feature, 
                "score": self._weight_feature(m)
                } 

        return str(snsapi_utils.JsonDict(ret))

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

    def tag_toggle(self, tag_id):
        cur_visible = self.tags_all[tag_id]['visible']
        cur = self.con.cursor()
        r = cur.execute('''
        UPDATE tag
        SET visible=?
        WHERE id=?
        ''', (1 - cur_visible, tag_id))
        logger.debug("Set tag %d to visibility %d", tag_id, 1 - cur_visible)
        self.refresh_tags()

    def tag_add(self, name):
        cur = self.con.cursor()
        r = cur.execute('''
        INSERT INTO tag(name, visible)
        VALUES(?, ?)
        ''', (name, 1))
        logger.debug("Add tag %s", name)
        self.refresh_tags()

    def get_tags(self):
        '''
        Only return visible tags

        '''
        return self.tags_visible

    def get_all_tags(self):
        return self.tags_all

    def refresh_tags(self):
        self.tags_all = {}
        self.tags_visible = {}
        cur = self.con.cursor()
        r = cur.execute('''
        SELECT id,name,visible,parent FROM tag  
        ''')
        for t in cur:
            self.tags_all[t[0]] = {
                    "id": t[0],
                    "name": t[1], 
                    "visible": t[2],
                    "parent": t[3], 
                    }
            if t[2] == 1:
                self.tags_visible[t[0]] = t[1]

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
        #TODO:
        #    Change the name!
        #    Final value used to rank should be called "score"
        #    This is distinguished from "weight". 
        return self.score.get_score(msg)

    def reweight(self, msg_id):
        cur = self.con.cursor()
        try:
            r = cur.execute('''
            SELECT pyobj FROM msg
            WHERE id=?
            ''', (msg_id,))
            m = self._str2pyobj(list(r)[0][0])
            w = self._weight_feature(m)
            t = int(self.time())
            r = cur.execute('''
            UPDATE msg
            SET weight=?,weight_time=?
            WHERE id=?
            ''', (w, t, msg_id))
        except Exception, e:
            logger.warning("Catch exception: %s", e)

    def reweight_all(self, younger_than = 86400):
        begin = self.time()
        cur = self.con.cursor()
        try:
            latest_time = int(self.time() - younger_than)
            r = cur.execute('''
            SELECT id from msg
            WHERE time >= ?
            ''', (latest_time, ))
            for m in r:
                self.reweight(m[0])
        except Exception, e:
            logger.warning("Catch exception: %s", e)
            return False
        end = self.time()
        logger.info("Reweight done. Time elapsed: %.2f", end - begin)
        return True

    def _dump2pickle(self, fn_pickle):
        # dump all to pickle format
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

    def _preprocess(self):
        import time

        # load
        begin = time.time()
        message = Serialize.loads(open('tmp/message.pickle').read())
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
        open('tmp/workspace.pickle', 'w').write(Serialize.dumps(message))
        end = time.time()
        print "Save finish. Time elapsed: %.3f" % (end - begin)

    def _tag_mapping(self):
        cur = self.con.cursor()
        r = cur.execute('''
        SELECT name,id from tag;
        ''')

        d = dict([(t[0],t[1]) for t in r])
        open('tmp/tag_mapping.json', 'w').write(json.dumps(d))

    def prepare_training_data(self):
        self._dump2pickle('tmp/message.pickle')
        self._preprocess()
        self._tag_mapping() 
        from analysis.select_samples import select_samples
        from analysis.select_samples import compute_order
        from analysis.select_samples import save_samples
        message = Serialize.loads(open('tmp/workspace.pickle').read())
        samples = select_samples(message)
        order = compute_order(samples)
        save_samples(samples, order, 'tmp/samples.pickle')
        return "done"

    def train(self, step = 10000):
        from analysis.autoweight import AutoWeight
        from analysis.autoweight import load_weights
        from analysis.autoweight import save_weights
        from analysis.autoweight import LearnerSigmoid
        data = Serialize.loads(open('tmp/samples.pickle').read())
        samples = data['samples']
        order = data['order']
        iweight = load_weights()
        aw = AutoWeight(samples, order, iweight, LearnerSigmoid())
        aw.sgd(step)
        save_weights(aw)
        self.score.load_weight()
        return "done"

if __name__ == '__main__':
    sp = SNSPocket()
    sp.load_config()
    sp.auth()

    q = SRFEQueue(sp)
    q.connect()
    q.refresh_tags()
    #q.input()

    #print sp.home_timeline()
