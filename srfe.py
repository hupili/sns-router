# -*- coding: utf-8 -*-

import sys
sys.path.append('bottle')
sys.path.append('snsapi')
from bottle import route, run, template, static_file, view, Bottle, request, response, redirect
from snsapi.snspocket import SNSPocket
from snsapi.snslog import SNSLog as logger
from snsapi import utils as snsapi_utils
from snsapi.utils import json

import time
import sqlite3

from queue import SRFEQueue
import threading

class AuthProxy(object):
    def __init__(self):
        super(AuthProxy, self).__init__()
        self.code_url = "((null))"
        self.requested_url = None
        self.current_channel = None

    def fetch_code(self):
        return self.code_url

    def request_url(self, url):
        self.requested_url = url
        self.code_url = "((null))"
        
ap = AuthProxy()
#print ap.code_url
#print ap.request_url
#ap.request_url("ss")
#print ap.requested_url
sp = SNSPocket()
sp.load_config()
for c in sp.values():
    c.request_url = lambda url: ap.request_url(url)
    c.fetch_code = lambda : ap.fetch_code()
    c.auth()
    #c.get_saved_token()

srfe = Bottle()

q = SRFEQueue(sp)
q.connect()
q.refresh_tags()

jsonconf = json.load(open('conf/srfe.json', 'r'))

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

def check_login(func):
    '''
    A decorator to check login. 
    Put it before those URLs where login is required. 
    '''
    def wrapper_check_login(*al, **ad):
        username = request.get_cookie("account", secret = jsonconf['cookie_sign_key'])
        if username is None or username != jsonconf['username']:
            redirect('/login')
        else:
            return func(*al, **ad)
    return wrapper_check_login

@srfe.route('/logout')
@view('logout')
def login_get():
    response.set_cookie("account", None, secret = jsonconf['cookie_sign_key'])
    return {}

@srfe.route('/login', method = 'GET')
@view('login')
def login_get():
    return {"state": "new"}

@srfe.route('/login', method = 'POST')
@view('login')
def login_post():
    username = request.forms.get('username')
    password = request.forms.get('password')
    if username == jsonconf['username'] and password == jsonconf['password']:
        response.set_cookie("account", username, secret = jsonconf['cookie_sign_key'])
        #return "Welcome %s! You are now logged in." % username
        return {"state": "succ"}
    else:
        return {"state": "fail"}
        #return "Login failed."

@srfe.route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static/')

@srfe.route('/')
@view('index')
@check_login
def index():
    return {}

@srfe.route('/config')
@view('config')
@check_login
def config():
    info = {}
    for ch in sp:
        info[ch] = sp[ch].jsonconf
        info[ch]['expire_after'] = int(sp[ch].expire_after())
        info[ch]['is_authed'] = sp[ch].is_authed()
    return {"info": info, "sp": sp, "ap": ap, "q": q}

@srfe.route('/config/tag/toggle/:tag_id')
@check_login
def config_tag_toggle(tag_id):
    q.tag_toggle(int(tag_id))
    redirect('/config')

@srfe.route('/auth/first/:channel_name')
@view('result')
@check_login
def auth_first(channel_name):
    op = "auth_first for %s" % (channel_name)
    ap.current_channel = channel_name
    sp[channel_name].auth_first()
    result = "request url: %s" % ap.requested_url
    redirect(ap.requested_url)
    return {'operation': op, 'result': result}

@srfe.route('/auth/second/')
@view('result')
@check_login
def auth_second():
    op = "auth_second for %s" % (ap.current_channel)
    qs = request.query_string
    # For compatibility with lower level interface. 
    # The snsbase parses code from the whole url. 
    ap.code_url = "http://snsapi.snsapi/auth/second/auth?%s" % qs
    sp[ap.current_channel].auth_second()
    sp[ap.current_channel].save_token()
    result = "done: %s" % qs
    return {'operation': op, 'result': result}

@srfe.route('/raw/:msg_id')
@view('result')
@check_login
def raw(msg_id):
    op = "check raw of message %s" % (msg_id)
    result = q.raw(msg_id)
    return {'operation': op, 'result': result}

@srfe.route('/why/:msg_id')
@view('result')
@check_login
def raw(msg_id):
    op = "check why of message %s" % (msg_id)
    result = q.why(msg_id)
    return {'operation': op, 'result': result}

@srfe.route('/flag/:fl/:msg_id')
@view('result')
@check_login
def flag(fl, msg_id):
    op = "flag %s as %s" % (msg_id, fl)
    result = q.flag(msg_id, fl)
    return {'operation': op, 'result': result}

@srfe.route('/tag/:tg/:msg_id')
@view('result')
@check_login
def tag(tg, msg_id):
    op = "tag %s as %s" % (msg_id, tg)
    result = q.tag(msg_id, tg)
    return {'operation': op, 'result': result}

@srfe.route('/home_timeline')
@view('home_timeline')
@check_login
def home_timeline():
    #sp.auth()
    #sl = sp.home_timeline(5)
    sl = q.output(20)
    #sl = q.output(30)
    meta = {
            "unseen_count": q.get_unseen_count()
            }
    return {'sl': sl, 'snsapi_utils': snsapi_utils, 'tags': q.get_tags(), 'meta': meta}
    #return template('home_timeline', sl = sl, snsapi_utils = snsapi_utils)

@srfe.route('/ranked_timeline')
@view('home_timeline')
@check_login
def ranked_timeline():
    sl = q.output_ranked(20, 86400)
    meta = {
            "unseen_count": q.get_unseen_count()
            }
    return {'sl': sl, 'snsapi_utils': snsapi_utils, 'tags': q.get_tags(), 'meta': meta}

@srfe.route('/sql', method = "GET")
@view('sql')
@check_login
def sql_get():
    return {}

@srfe.route('/sql', method = "POST")
@view('sql')
@check_login
def sql_post():
    condition = request.forms.get('condition').strip()
    sl = q.sql(condition)
    return {'sl': sl, 'snsapi_utils': snsapi_utils, \
            'tags': q.get_tags(), 'submit': True, 'condition': condition}

@srfe.route('/update', method = 'GET')
@view('update')
@check_login
def update_get():
    return {}

@srfe.route('/update', method = 'POST')
@view('update')
@check_login
def update_post():
    sp.auth()
    status = request.forms.get('status')
    status = snsapi_utils.console_input(status)
    result = sp.update(status)
    return {'result': result, 'status': status, 'submit': True}

@srfe.route('/forward/:msg_id', method = 'POST')
@view('result')
@check_login
def forward_post(msg_id):
    sp.auth()
    comment = request.forms.get('comment')
    comment = snsapi_utils.console_input(comment)
    op = "forward status '%s' with comment '%s'" % (msg_id, comment)
    #result = "s"
    result = q.forward(msg_id, comment)
    return {'result': result, 'operation': op}

ith = InputThread(q)
# The following option make the thread end when our 
# Bottle server ends. 
# Ref: http://stackoverflow.com/questions/3788208/python-threading-ignores-keyboardinterrupt-exception
ith.daemon=True
ith.start()
#srfe.run(host='localhost', port=8080, debug = True, reloader = True)
#srfe.run(host='localhost', port=8080, debug = True)

srfe.run(host = jsonconf.get('host', '127.0.0.1'),\
        port = jsonconf.get('port', 8080),\
        debug = jsonconf.get('debug', True))
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
