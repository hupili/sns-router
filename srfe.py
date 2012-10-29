# -*- coding: utf-8 -*-

import sys
sys.path.append('bottle')
sys.path.append('snsapi')
from bottle import route, run, template, static_file, view, Bottle, request
from snsapi.snspocket import SNSPocket
from snsapi import utils as snsapi_utils
import sqlite3

from queue import SRFEQueue

sp = SNSPocket()
sp.load_config()
sp.auth()

srfe = Bottle()

q = SRFEQueue(sp)
q.connect()

@srfe.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static/')

@srfe.route('/home_timeline')
@view('home_timeline')
def home_timeline():
    #sp.auth()
    #sl = sp.home_timeline(5)
    sl = q.output(5)
    return {'sl': sl, 'snsapi_utils': snsapi_utils}
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

srfe.run(host='localhost', port=8080, debug = True, reloader = True)

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
