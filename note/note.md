# SNS Router Development Notes

## Framework Survey

I want to use web UI, so that SNSRouter 
can be used on nearly any device. 
In the first step, I launch the HTTP server locally. 
This is for prototyping convenience. 
Later, the codes should be able to move to a 
real dedicated HTTP server with least modification. 

[http://stackoverflow.com/questions/877033/how-can-i-create-an-local-webserver-for-my-python-scripts](http://stackoverflow.com/questions/877033/how-can-i-create-an-local-webserver-for-my-python-scripts)

SimpleHTTPSever and BaseHTTPServer may help. 

[http://docs.python.org/library/wsgiref.html](http://docs.python.org/library/wsgiref.html)

WSGI? Looks more extensible. 

[http://stackoverflow.com/questions/13060853/extensible-local-http-server-with-framework-in-python](http://stackoverflow.com/questions/13060853/extensible-local-http-server-with-framework-in-python)

my questions. 

As pointed out, Bottle and Flask are worth to look at. 
At first sight, the single file aspect of Bottle is attractive for me. 
On the other hand, Flask provides some handy plugins like distributed message queuing. 

[http://www.slideshare.net/r1chardj0n3s/web-microframework-battle](http://www.slideshare.net/r1chardj0n3s/web-microframework-battle)

The survey of Micro-frameworks, Richard Jones. 

[http://www.youtube.com/watch?v=AYjPIMe0BhA](http://www.youtube.com/watch?v=AYjPIMe0BhA)

The survey of Micro-frameworks, Richard Jones. Youtube Video. 

## Serialization

[http://www.youtube.com/watch?v=G-lGCC4KKok](http://www.youtube.com/watch?v=G-lGCC4KKok)

In the talk given by Youtube designer, he shared some experience on 
making Youtube scalable. 
Very interesting. 
One thing about serialization is to not use pickle, 
which is in the standard library and currently used in SNSRouter's queue infrastructure. 
Efficiency is not a major concern in my current project. 
We have at least one upgrade choice: import cPickle as pickle. 

## Preliminary Data (20121108)

```
sqlite> select count(*) from msg;
7404
sqlite> select count(*) from msg where flag="seen";
2994
sqlite> select count(*) from msg_tag;
343
sqlite> select count(*) from log;
4535
sqlite> select count(*) from log where operation like "%forward%";
55
sqlite> select name,count(*) from msg_tag,tag where tag_id = tag.id group by tag_id;
null|2
mark|84
gold|2
silver|16
bronze|10
news|75
interesting|27
shit|26
nonsense|101
```

Line of code (20121108): 5523
