# -*- coding: utf-8 -*-

# Evaluation using Kendall's tau correlation coefficient
# http://en.wikipedia.org/wiki/Kendall_tau_rank_correlation_coefficient
#
# Note that we only have partial order, so the denominator is different. 

import sys
sys.path.append('../bottle')
sys.path.append('../snsapi')
import snsapi
from snsapi.snspocket import SNSPocket
from snsapi.platform import SQLite
from snsapi import utils as snsapi_utils
from snsapi.utils import json
from snsapi import snstype
# On my server, pickle uses 24s to load 
# cPickle uses 6s to load. 
# very significant
#from snsapi.utils import Serialize
import cPickle as Serialize
from snsapi.snsbase import SNSBase
from snsapi.snslog import SNSLog as logger

import base64
import hashlib
import sqlite3

import networkx as nx

def load_pickle(fn):
    import time
    begin = time.time()
    pk_obj = Serialize.loads(open(fn).read())
    end = time.time()
    print "Load '%s' finish. Time elapsed: %.3f" % (fn, end - begin)
    return pk_obj

def evaluate_kendall(ranking, order):
    '''
    Kendall's tau

    rankding: A list containing message IDs in ranked order. 
    order: A list containing preference pairs. 

    '''
    total = len(order)
    conc = 0 
    disc = 0 

    d_rank = {}
    for i in range(0, len(ranking)):
        d_rank[ranking[i]] = i

    for (i,j) in order:
        if d_rank[i] < d_rank[j]: 
            conc += 1
        if d_rank[i] > d_rank[j]: 
            disc += 1

    #for i in samples.itervalues():
    #    for j in samples.itervalues():
    #        if ranking[i].tags != ranking[j].tags:
    #            total += 1 
    #            if is_inorder(rel_gt, ranking[i].tags.keys(), ranking[j].tags.keys()):
    #                conc += 1
    #            if is_inorder(rel_gt, ranking[j].tags.keys(), ranking[i].tags.keys()):
    #                disc += 1

    print "total:%d; conc:%d; disc:%d" % (total, conc, disc)
    return 1.0 * (conc - disc) / total

if __name__ == '__main__':
    samples = load_pickle('samples.pickle')
    ret = evaluate_kendall(samples['samples'].keys(), samples['order'])
    print ret
