# -*- coding: utf-8 -*-

# A sample hooks file. 
# To customize, copy this file to ``myhooks.py`` and edit further

import sys
sys.path.append('snsapi')
import snsapi
from snsapi.snslog import SNSLog as logger

distribute_conf = {
  "description": "Use this channel to distribute your aggregated timeline", 
  "platform": "RSS2RW", 
  "url": "distribute.rss", 
  "channel_name": "new_channel_name", 
  "message": {
    "timezone_correction": None
  }, 
  "open": "yes", 
  "methods": "update",
  "author": "hpl",
  "user_name": "hpl",
  "entry_timeout": 2592000
}

distribute = snsapi.platform.RSS2RW(distribute_conf)


def hook_new_message(q, msg):
    mymsg = False
    sp = q.sp
    for ch in sp.values():
        if 'user_name' in ch.jsonconf:
            user_name = ch.jsonconf['user_name']
            if user_name == msg.parsed.username:
                mymsg = True
    if mymsg:
        logger.debug('distribute message: %s', msg)
        distribute.update(msg)

if __name__ == '__main__':
    from snsapi import snspocket, snstype
    sp = snspocket.SNSPocket()
    sp.add_channel(distribute_conf)
    #sp.load_config()
    sp.auth()
    from queue import SRFEQueue
    q = SRFEQueue(sp)
    q.connect()
    q.refresh_tags()

    import time
    m1 = snstype.Message({'text': 'test', 
        'username': 'hpl', 
        'userid': 'hpl', 
        'time': time.time() })

    #hook_new_message(q, m1)
    q._inqueue(m1)
