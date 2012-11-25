# -*- coding: utf-8 -*-

# The return is 401???
# 'Consumer key refused??'
# Why is it a headache to get all the face icons? 

# http://open.weibo.com/wiki/Emotions 
# http://api.t.sina.com.cn/emotions.json

import sys
sys.path.append('../../')
sys.path.append('../../bottle')
sys.path.append('../../snsapi')
import snsapi
from snsapi.snspocket import SNSPocket
from snsapi.platform import SQLite
from snsapi import utils as snsapi_utils
from snsapi import snstype
import cPickle as Serialize
from snsapi.snsbase import SNSBase
from snsapi.snslog import SNSLog as logger

import base64
import hashlib
import sqlite3

if __name__ == '__main__':
    conf = snsapi_utils.json.load(open('../conf/channel.json'))
    sina = None
    for c in conf:
        if c['platform'] == "SinaWeiboStatus":
            sina = snsapi.platform.SinaWeiboStatus(c)

    if sina is None:
        print "Can not find SinaWeiboStatus platform"
    else:
        sina.auth()
        url = 'http://api.t.sina.com.cn/emotions.json'
        params = {}
        #params['access_token'] = sina.token.access_token
        params['source'] = sina.jsonconf['app_key']
        ret = sina._http_post(url, params)
        print ret
