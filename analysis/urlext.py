# -*- coding: utf-8 -*-

import re

def url_extract(text):
    # We consider only the standard url without CN characters
    # Refs:
    #    * http://stackoverflow.com/questions/140549/what-character-set-should-i-assume-the-encoded-characters-in-a-url-to-be-in
    #    * http://www.ietf.org/rfc/rfc1738.txt
    ret = {}
    # 0x00-0x1F is control character
    # 0x20 is blankspace
    # 0x7F is control character
    r = re.compile(r'https?://[\x21-\x7E]+') 
    l = r.findall(text)
    if not l is None:
        ret['urls'] = l
    else:
        ret['urls'] = []
    t = text
    for u in ret['urls']:
        t = t.replace(u, ' ')
    ret['text'] = t
    return ret

if __name__ == '__main__':
    while (True):
        try:
            text = raw_input()
            ret = url_extract(text)
            print "text:"
            print text
            print "urls:"
            for u in ret['urls']:
                print u
            print "cleaned text:"
            print ret['text']
        except EOFError:
            break
