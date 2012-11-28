# -*- coding: utf-8 -*-
#
# Select samples from 'workspace.pickle' to train weights automatically. 
#

import sys
sys.path.append('../bottle')
sys.path.append('../snsapi')
import snsapi
from snsapi.snspocket import SNSPocket
from snsapi.platform import SQLite
from snsapi import utils as snsapi_utils
from snsapi import snstype
from snsapi.utils import json
import cPickle as Serialize
from snsapi.snsbase import SNSBase
from snsapi.snslog import SNSLog as logger

import networkx as nx

import base64
import hashlib
import sqlite3
import random

# Number of 'null' labeled messages to extract
NULL_SAMPLES = 800

def select_samples(message):
    candidates = {}
    null_msg = []

    for m in message['seen_list']:
        if len(m.tags) >= 1:
            #candidates.append(m)
            candidates[m.msg_id] = m
        else:
            null_msg.append(m)

    prob = float(NULL_SAMPLES) / (len(message['seen_list']) - len(candidates))
    if prob > 1.0:
        prob = 1.0
    print "Selecting null message probability: %.3f" % (prob)

    for m in null_msg:
        if random.random() < prob:
            m.tags = {"null": 1}
            #candidates.append(m)
            candidates[m.msg_id] = m

    print "Total %d samples extracted" % (len(candidates))
    return candidates

def get_gt_relation():
    '''
    Get the Greater-Than relation from user defined preference. 

    Perfrom graph induction to calculate as many pairs as possible.

    '''
    # Load preference
    json_autoweight = json.load(open('conf/autoweight.json'))
    preference = json_autoweight['preference']
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
    # Optimistic evaluation:
    #    * One msg has multiple tags. 
    #    * As long as one tag agrees the order, we say "concordant"
    order = False
    for t1 in list_t1:
        for t2 in list_t2:
            if (t1, t2) in rel_gt:
                order = True
    return order
    #if (list_t1[0], list_t2[0]) in rel_gt:
    #    return True
    #else:
    #    return False

def compute_order(samples):
    '''
    Generate all Greater-Than order pairs

    '''
    rel_gt = get_gt_relation()
    total = 0
    order = []
    for i in samples.itervalues():
        for j in samples.itervalues():
            if i != j and i.tags != j.tags:
                total += 1 
                if is_inorder(rel_gt, i.tags.keys(), j.tags.keys()):
                    order.append((i.msg_id, j.msg_id))
    return order

if __name__ == '__main__':
    import time
    begin = time.time()
    message = Serialize.loads(open('workspace.pickle').read())
    end = time.time()
    print "Load finish. Time elapsed: %.3f" % (end - begin)

    print "Start to extract samples"
    samples = select_samples(message)
    
    print "Start to compute order"
    order = compute_order(samples)
    
    open('samples.pickle', 'w').write(Serialize.dumps({\
            "samples": samples,\
            "order": order,\
            }))
