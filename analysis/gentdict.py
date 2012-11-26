# -*- coding: utf-8 -*-
# Generate topic dict based on:
#    {Topic Frequency} * {Inverse Whole Frequency}

import cPickle as Serialize
import re

def load_dict(path):
    '''
    Format of dict:
    \d+ \w
    {freq} {term}

    '''
    d = {}
    with open(path, 'r') as fp:
        for line in fp:
            r = re.compile(r'^\s*(\d+) (.+)$')
            m = r.match(line)
            if m:
                freq = float(m.groups()[0])
                term = m.groups()[1]
                #print freq
                #print term
                d[term] = freq
    return d

def weight(dict_all, dict_topic):
    '''
    {Topic Frequency} * {Inverse Whole Frequency}
    '''
    w_total = 0.0
    for term in dict_topic:
        try:
            dict_topic[term] /= dict_all[term]
            w_total += dict_topic[term]
        except KeyError, e:
            pass
            #print e.message
    for term in dict_topic:
        dict_topic[term] /= w_total

if __name__ == '__main__':
    d_all = load_dict('kdb/term.all')
    d_tech = load_dict('kdb/term.mark.tech')
    d_news = load_dict('kdb/term.mark.news')
    d_interesting = load_dict('kdb/term.mark.interesting')
    d_nonsense = load_dict('kdb/term.mark.nonsense')
    
    weight(d_all, d_tech)
    weight(d_all, d_news)
    weight(d_all, d_interesting)
    weight(d_all, d_nonsense)

    tdict = {
            'tech': d_tech,
            'news': d_news,
            'interesting': d_interesting,
            'nonsense': d_nonsense,
            }

    with open('kdb/tdict.pickle', 'w') as fp:
        fp.write(Serialize.dumps(tdict))

