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

    #count = 0
    #for m in pk_obj:
    #    if len(m.tags) < 1:
    #        #print m
    #        count += 1
    #print count

    return pk_obj

def graph_induction(preference):
    # tag name to id
    tag_mapping = json.load(open('tag_mapping.json'))
    edges = []
    for p in preference:
        if p[0] in tag_mapping and p[1] in tag_mapping:
            edges.append((tag_mapping[p[0]], tag_mapping[p[1]]))

    g = nx.DiGraph()
    g.add_edges_from(edges)
    paths = nx.shortest_paths.unweighted.all_pairs_shortest_path(g)
    rel_gt = {}
    for u in paths:
        for v in paths[u]:
             rel_gt[(u, v)] = 1

    return rel_gt

def is_inorder(rel_gt, list_t1, list_t2):
    if (list_t1[0], list_t2[0]) in rel_gt:
        return True
    else:
        return False
    ## Optimistic evaluation:
    ##    * One msg has multiple tags. 
    ##    * As long as one tag agrees the order, we say "concordant"
    #order = False
    #for t1 in list_t1:
    #    for t2 in list_t2:
    #        if (t1, t2) in rel_gt:
    #            order = True
    #return order


def evaluate_kendall(fn_ranking):
    ranking = load_pickle(fn_ranking)
    json_autoweight = json.load(open('conf/autoweight.json'))
    preference = json_autoweight['preference']
    rel_gt = graph_induction(preference)

    conc = 0 # in order
    disc = 0 # reversed order

    total = 0 # number of to be compared pairs
    n = len(ranking)
    for i in range(0, n - 1):
        for j in range(i+1, n):
            if ranking[i].tags != ranking[j].tags:
                total += 1 
                if is_inorder(rel_gt, ranking[i].tags.keys(), ranking[j].tags.keys()):
                    conc += 1
                if is_inorder(rel_gt, ranking[j].tags.keys(), ranking[i].tags.keys()):
                    disc += 1

    return 1.0 * (conc - disc) / total
    #return 1.0 * (conc - disc) / (n * (n-1) / 2)

if __name__ == '__main__':
    ret = evaluate_kendall('ranking.pickle')
    print ret
