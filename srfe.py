# -*- coding: utf-8 -*-

import sys
sys.path.append('bottle')
sys.path.append('snsapi')
from bottle import route, run, template, static_file, view, Bottle, request
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger
from snsapi import utils as snsapi_utils

import time
import sqlite3

from queue import SRFEQueue
import threading

sp = SNSPocket()
sp.load_config()
sp.auth()

srfe = Bottle()

q = SRFEQueue(sp)
q.connect()

class InputThread(threading.Thread):
    def __init__(self, queue):
        super(InputThread, self).__init__()
        self.queue = queue
        self.keep_running = True

    def run(self):
        while (self.keep_running):
            self.queue.input()
            logger.debug("Invoke input() on queue")
            time.sleep(60 * 5) # 5 Minutes per fetch 

@srfe.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static/')

@srfe.route('/')
@view('index')
def index():
    return {}

@srfe.route('/flag/:fl/:msg_id')
@view('result')
def flag(fl, msg_id):
    op = "flag %s as %s" % (msg_id, fl)
    result = q.flag(msg_id, fl)
    return {'operation': op, 'result': result}

@srfe.route('/tag/:tg/:msg_id')
@view('result')
def flag(tg, msg_id):
    op = "tag %s as %s" % (msg_id, tg)
    result = q.tag(msg_id, tg)
    return {'operation': op, 'result': result}

@srfe.route('/home_timeline')
@view('home_timeline')
def home_timeline():
    #sp.auth()
    #sl = sp.home_timeline(5)
    sl = q.output(50)
    return {'sl': sl, 'snsapi_utils': snsapi_utils, 'tags': q.get_tags()}
    #return template('home_timeline', sl = sl, snsapi_utils = snsapi_utils)

@srfe.route('/update', method = 'GET')
@view('update')
def update_get():
    return {}

@srfe.route('/update', method = 'POST')
@view('update')
def update_post():
    sp.auth()
    status = request.forms.get('status')
    status = snsapi_utils.console_input(status)
    result = sp.update(status)
    return {'result': result, 'status': status, 'submit': True}

ith = InputThread(q)
# The following option make the thread end when our 
# Bottle server ends. 
# Ref: http://stackoverflow.com/questions/3788208/python-threading-ignores-keyboardinterrupt-exception
ith.daemon=True
ith.start()
#srfe.run(host='localhost', port=8080, debug = True, reloader = True)
srfe.run(host='localhost', port=8080, debug = True)
ith.keep_running = False


#@srfe.route('/')
#@srfe.route('/hello/:name')
#@view('echo')
#def index(name='World'):
#    return {"response": name}
#    #return template('<b>Hell {{name}}</b>!', name=name)

#@route('/:path')
#def default(path = None):
#    return template('<red> {{path}} </red>', path = path)


# Use the line to disable catching "Internal Server Erros"
#bottle.app().catchall = False

#run(host='localhost', port=8080)
#run(host='192.168.64.88', port=8080)
