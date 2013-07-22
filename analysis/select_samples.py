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

#See the comments in 'autoweight.py'
#from feature import Feature
from os import path
_dir_root = path.dirname(path.dirname(path.abspath(__file__)))
print _dir_root
sys.path.insert(0, _dir_root)
from ranking.feature import Feature


import networkx as nx

import base64
import hashlib
import sqlite3
import random

def select_samples(message):
    candidates = {}
    null_msg = []

    for m in message['seen_list']:
        if len(m.tags) >= 1:
            #candidates.append(m)
            candidates[m.msg_id] = m
        else:
            null_msg.append(m)

    # Sample same number of null tag messages
    prob = float(len(candidates)) / (len(message['seen_list']) - len(candidates))
    if prob > 1.0:
        prob = 1.0
    print "Selecting null message probability: %.3f" % (prob)

    for m in null_msg:
        if random.random() < prob:
            #m.tags = {"null": 1}
            # All tag id is greater than or equal to 1. 
            # 0 is reserved as "null" tag if the user has not defined one. 
            m.tags = {0: 1}
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
    tag_mapping = json.load(open('tmp/tag_mapping.json'))
    #if not 'null' in tag_mapping:
    #    tag_mapping['null'] = 0 
    # Force 0 to be the 'null' tag_id
    # User defined 'null' is not effective. 
    tag_mapping['null'] = 0 
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

def divide_samples(samples, training_ratio = 0.5):
    N = len(samples)
    shuffled = sorted(samples.keys(), key = lambda m: random.random())
    training = {}
    testing = {}
    for i in range(0, int(N * training_ratio)):
        training[shuffled[i]] = samples[shuffled[i]]
    for i in range(int(N * training_ratio), N):
        testing[shuffled[i]] = samples[shuffled[i]]
    return {"training": training, "testing": testing}

def save_samples(samples, order, fn_out):
    open(fn_out, 'w').write(Serialize.dumps({\
            "samples": samples,\
            "order": order,\
            }))

def export_arff(message_list, ds_name, fn_arff):
    '''
    Export message_list to Weka's arff file

    ds_name: the name of data set. Shown in first line 
             of arff file.
    '''

    all_tags = json.loads(open('tag_mapping.json').read())
    all_tags_r = {}
    for (k, v) in all_tags.iteritems():
        all_tags_r[v] = k
    all_tags_r[0] = "null"

    with open(fn_arff, 'w') as fp:
        fp.write("@relation %s\n\n" % (ds_name))
        fn = []

        # Write schema
        fp.write("@attribute id numeric\n")
        for fe in Feature.feature_extractors:
            for (f, t) in fe.schema.iteritems():
                fp.write("@attribute %s %s\n" % (f, t))
                fn.append(f)
        fp.write("@attribute class {%s}\n" % (",".join(all_tags.keys())))

        # Write data
        fp.write("\n\n@data\n")
        for m in message_list:
            # Ignore multi tagged messages for simplicity
            if len(m.tags) == 1:
                i = str(m.msg_id)
                t = all_tags_r[m.tags.keys()[0]]
                Feature.extract(m)
                fields = [str(m.feature[f]) for f in fn]
                fields.insert(0, i)
                fields.append(t)
                fp.write(",".join(fields) + "\n")

if __name__ == '__main__':
    import time
    begin = time.time()
    message = Serialize.loads(open('workspace.pickle').read())
    end = time.time()
    print "Load finish. Time elapsed: %.3f" % (end - begin)

    print "Start to extract samples"
    samples = select_samples(message)
    print "Export to weka"
    export_arff(samples.values(), 'snsrouter', 'weka/snsrouter.arff')
    print "Export to weka, done"

    print "Divide into training and testing set"
    ret = divide_samples(samples, 0.5)
    training_samples = ret['training']
    testing_samples = ret['testing']
    
    print "Start to compute order for training set"
    training_order = compute_order(training_samples)

    print "Start to compute order for testing set"
    testing_order = compute_order(testing_samples)

    print "Save to file"
    save_samples(training_samples, training_order, 'training_samples.pickle')
    export_arff(training_samples.values(), 'snsrouter-training', 'weka/snsrouter-training.arff')
    save_samples(testing_samples, testing_order, 'testing_samples.pickle')
    export_arff(testing_samples.values(), 'snsrouter-testing', 'weka/snsrouter-testing.arff')
    
    print "Training samples: %d" % len(training_samples)
    print "Training order: %d" % len(training_order)
    print "Testing samples: %d" % len(testing_samples)
    print "Testing order: %d" % len(testing_order)
