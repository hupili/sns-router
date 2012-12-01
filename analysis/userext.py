# -*- coding: utf-8 -*-

import re

def user_extract(text):
    # v6
    #separator = [u'，', u'：', u'；', u'！', u'）', u'（', u'《', u'》', u'】', u'【', u'。']
    separator = [u"，：；！）（《》】【。"]
    ret = {}
    # v1
    #r = re.compile(r'(@.+?)( |$)')
    # v2
    #r = re.compile(r'(@.+?)([ :,\(]|$)')
    # v3
    #r = re.compile(r'(@.+?)([ :,\(\|$])')
    # v4
    r = re.compile(r'((转自|@)[^@ ]+?)([\s:;,\(\|$\[\]\(\)/])')
    l = r.finditer(text)
    ret['users'] = []
    if not l is None:
        for m in l:
            u = m.groups()[0].decode('utf-8')
            #print u
            # v5
            for s in separator:
                i = u.find(s)
                if i != -1:
                    u = u[:i] 
                #print u
            ret['users'].append(u.encode('utf-8'))
    t = text
    for u in ret['users']:
        t = t.replace(u, ' ')
    ret['text'] = t
    return ret

if __name__ == '__main__':
    while (True):
        try:
            text = raw_input()
            print "text:"
            print text
            ret = user_extract(text)
            print "users:"
            for u in ret['users']:
                print u
            print "cleaned text:"
            print ret['text']
        except EOFError:
            break
