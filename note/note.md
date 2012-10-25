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
