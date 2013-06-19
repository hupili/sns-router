# Debug notes

## Support timeout in fetch home timeline

The following pice is workable:

```
    def _home_timeline_direct(self, channel):
        return self.sp.home_timeline(channel)

    def _home_timeline(self, time_wait, channel):
        logger.debug("channel '%s', timeout '%s'", channel, time_wait)
        if time_wait is None:
            return self.sp.home_timeline(channel=channel)
        else:
            func = timeout(time_wait)(self._home_timeline_direct)
            try:
                return func(channel=channel)
            except TimeoutException:
                logger.warning("channel '%s' read hometimeline timeout.", channel)
                return snstype.MessageList()
```

The following piece will raise error:

```
    def _home_timeline(self, time_wait, channel):
        logger.debug("channel '%s', timeout '%s'", channel, time_wait)
        if time_wait is None:
            return self.sp.home_timeline(channel=channel)
        else:
            func = timeout(time_wait)(self.sp.home_timeline)
            try:
                return func(channel=channel)
            except TimeoutException:
                logger.warning("channel '%s' read hometimeline timeout.", channel)
                return snstype.MessageList()
```

Following is the error message:

```
[DEBUG][20130619-142928][queue.py][_home_timeline][241]channel 'ch89. OpenHero 开勇', timeout '40'
[INFO][20130619-142932][snspocket.py][home_timeline][275]Read 20 statuses
Traceback (most recent call last):
  File "/usr/lib64/python2.7/multiprocessing/queues.py", line 242, in _feed
    send(obj)
  File "/usr/lib/python2.7/site-packages/BeautifulSoup.py", line 439, in __getnewargs__
    return (NavigableString.__str__(self),)
  File "/usr/lib/python2.7/site-packages/BeautifulSoup.py", line 455, in __str__
    return self.encode(encoding)
RuntimeError: maximum recursion depth exceeded while calling a Python object
^CTraceback (most recent call last):
  File "test.py", line 13, in <module>
    print q._home_timeline(40, channel=u'ch89. OpenHero 开勇')
  File "/home/plhu/research/sns-router-rss/queue.py", line 247, in _home_timeline
    return func(channel=channel)
  File "snsapi/snsapi/third/timeout.py", line 75, in inner
    success, result = proc.result()
  File "snsapi/snsapi/third/timeout.py", line 59, in result
    return self.queue.get()
  File "/usr/lib64/python2.7/multiprocessing/queues.py", line 91, in get
    res = self._recv()
KeyboardInterrupt
```

For the record, this is the channel to trigger the error:

```
  {
    "url": "http://blog.csdn.net/OpenHero/Rss.aspx", 
    "platform": "RSSSummary", 
    "__other__info": {
      "text": "OpenHero \u5f00\u52c7", 
      "html_url": "http://blog.csdn.net/openhero"
    },   
    "open": "yes", 
    "channel_name": "ch89. OpenHero \u5f00\u52c7"
  },   
```

This is a test script `test.py`:

```
# -*- coding: utf-8 -*-

from queue import *

sp = SNSPocket()
sp.load_config()
sp.auth()

q = SRFEQueue(sp)
q.connect()
q.refresh_tags()

print q._home_timeline(40, channel=u'ch89. OpenHero 开勇')
```
