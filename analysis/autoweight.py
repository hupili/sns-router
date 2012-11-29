# -*- coding: utf-8 -*-

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

from feature import Feature
from evaluation import evaluate_kendall

import base64
import hashlib
import sqlite3
import random
import numpy

class Learner(object):
    """
    Base class for a learner
    
    One can implement different objective and gradient here
    """
    def __init__(self):
        super(Learner, self).__init__()

    def objective(self, X, w, order):
        pass

    def gradient(self, X, w, order):
        pass

class LearnerSigmoid(Learner):
    def __init__(self):
        super(LearnerSigmoid, self).__init__()
        
    def _S(self, t):
        #coeff = 10.0
        coeff = 100.0
        #coeff = 1000.0
        return 1.0 / (1.0 + numpy.exp(- coeff * t))
    
    def _dS(self, t):
        return self._S(t) * (1 - self._S(t))

    def _Gij(self, xi, xj, w):
        '''
        Compute per pair gradient

        xi, xj: data points
        w: current weights

        xi, xj, and w are all lists
        '''
        inner = 0.0
        for k in range(len(w)):
            inner += (xi[k] - xj[k]) * w[k]
        part2 = self._dS(inner)
        ret = []
        for k in range(len(w)):
            ret.append(-(xi[k] - xj[k]) * part2)
        return ret

    def _G(self, X, w, order):
        '''
        Compute full gradient

        X: A dict of data points. 
           * values: One data point is a list.
           * keys: msg_id from database. 
        w: current weights
        order: derived order (edges on priority graph)
        '''
        #N = 1.0 * len(order)
        G = [0] * len(w)
        for (i,j) in order:
            Gij = self._Gij(X[i], X[j], w)
            for k in range(len(w)):
                #G[k] += (Gij[k] / N)
                G[k] += Gij[k] 
        return G

    def objective(self, X, w, order):
        #N = 1.0 * len(order)
        o = 0.0
        for (i,j) in order:
            inner = 0.0
            for k in range(len(w)):
                inner += (X[i][k] - X[j][k]) * w[k]
            #o += (1 - self._S(inner)) / N
            o += (1 - self._S(inner)) 
        return o

    def gradient(self, X, w, order):
        return self._G(X, w, order)

    def _line_obj(self, coeff, alpha):
        o = 0.0
        for v in coeff.values():
            o += 1 - self._S(v['a'] + v['b'] * alpha)
        return o

    def line_search(self, X, w, order, g):
        alpha = 1.0
        coeff = {}
        for (i,j) in order:
            a = 0.0
            b = 0.0
            for k in range(len(w)):
                a += (X[i][k] - X[j][k]) * w[k]
                b += (X[i][k] - X[j][k]) * g[k]
            coeff[(i,j)] = {'a': a, 'b': b}
        orig_line_obj = self._line_obj(coeff, 0.0)
        print "origin line obj: %.7f" % orig_line_obj
        while alpha > 1.0 / len(X):
            print "alpha: %.7f" % alpha
            cur_line_obj = self._line_obj(coeff, -alpha)
            print "line obj: %.7f" % cur_line_obj
            alpha /= 2
            if cur_line_obj < orig_line_obj:
                return alpha
        return alpha
        
class LearnerSquareSigmoid(Learner):
    """docstring for LearnerSquareSigmoid"""
    def __init__(self):
        super(LearnerSquareSigmoid, self).__init__()
        
    def _S(self, t):
        return 1.0 / (1.0 + numpy.exp(-t))
    
    def _dS(self, t):
        return self._S(t) * (1 - self._S(t))

    def _Gij(self, xi, xj, w):
        '''
        Compute per pair gradient

        xi, xj: data points
        w: current weights

        xi, xj, and w are all lists
        '''
        inner = 0.0
        for k in range(len(w)):
            inner += (xi[k] - xj[k]) * w[k]
        part1 = 2.0 * (self._S(inner) - 1)
        part2 = self._dS(inner)
        ret = []
        for k in range(len(w)):
            ret.append((xi[k] - xj[k]) * part1 * part2)
        return ret

    def _G(self, X, w, order):
        '''
        Compute full gradient

        X: A dict of data points. 
           * values: One data point is a list.
           * keys: msg_id from database. 
        w: current weights
        order: derived order (edges on priority graph)
        '''
        #N = 1.0 * len(order)
        G = [0] * len(w)
        for (i,j) in order:
            Gij = self._Gij(X[i], X[j], w)
            for k in range(len(w)):
                #G[k] += (Gij[k] / N)
                G[k] += Gij[k] 
        return G

    def objective(self, X, w, order):
        #N = 1.0 * len(order)
        o = 0.0
        for (i,j) in order:
            inner = 0.0
            for k in range(len(w)):
                inner += (X[i][k] - X[j][k]) * w[k]
            #o += (self._S(inner) - 1) ** 2 / N
            o += (self._S(inner) - 1) ** 2 
        return o

    def gradient(self, X, w, order):
        return self._G(X, w, order)

class AutoWeight(object):
    """docstring for AutoWeight"""

    def __init__(self, samples, order, init_weight, learner):
        super(AutoWeight, self).__init__()
        self.samples = samples
        self.order = order
        self.learner = learner
        if init_weight is None:
            # Use one of the samples keys as sets of features to be trained. 
            # This is deprecated. Whenever possible, please init your features
            # with weight in 'weights.json'
            m = samples.values()[0]
            Feature.extract(m)
            self.feature_name = m.feature.keys()
        else:
            self.feature_name = init_weight.keys()
        self.X = self.msg2X(samples)
        if init_weight is None:
            self.w = self.initw(self.init_weight_kendall(self.feature_name, self.samples, self.order))
        else:
            self.w = self.initw(init_weight)

    def _weight_feature(self, msg):
        Feature.extract(msg)
        score = 0.0
        for i in range(len(self.feature_name)):
            f = self.feature_name[i]
            w = self.w[i]
            if f in msg.feature:
                score += msg.feature[f] * w
        return score

    def normalize(self, w):
        t = 0.0
        for i in w:
            t += i * i
        t = numpy.sqrt(t)
        if t < 1e-5:
            t = 1.0
        return [i / t for i in w]

    def normalize_sum(self, w):
        t = 0.0
        for i in w:
            t += i
        t = numpy.sqrt(t)
        if numpy.abs(t) < 1e-5:
            t = 1.0
        return [i / t for i in w]

    def initw(self, init_weight):
        w = []
        for name in self.feature_name:
            w.append(init_weight[name])
        #return self.normalize(w)
        return w

    def msg2X(self, samples):
        '''
        Convert messages to data matrix format. 

        X: A dict. See explanation of _G()
        '''
        X = {}
        for m in samples.values():
            Feature.extract(m)
            x = []
            for name in self.feature_name:
                x.append(m.feature[name])
            X[m.msg_id] = x
        return X

    @snsapi_utils.report_time
    def sgd(self):
        M = len(self.order)
        last_obj = self.learner.objective(self.X, self.w, self.order)
        for i in range(1, M):
            tmp = []
            tmp.append(self.order[random.randint(0, M-1)])
            g = self.learner.gradient(self.X, self.w, tmp)
            g = self.normalize(g)
            #print "Stochastic Gradient: %s" % g
            #a = self.learner.line_search(self.X, self.w, self.order, g)
            a = 1e-3
            #print "Step size: %.7f" % a
            new_w = []
            for k in range(len(self.w)):
                new_w.append(self.w[k] - a * g[k])
            self.w = new_w
            #print "%d" % i
            if i % 10000 == 0:
                print "Round %d" % i
                new_obj = self.learner.objective(self.X, new_w, self.order)
                print "Obj: %.7f" % new_obj
                if abs(new_obj - last_obj) / last_obj < 1e-4:
                    print "Small gap, termiante"
                    break
            #print "Kendall's score %.7f" % self.evaluate()
        print "Terminate due to maximum number of rounds"

        return self.dictw()
        
        # Pre Test sections
        #g = self.learner.gradient(self.X, self.w, self.order)
        #g = self.normalize(g)
        #print "Full Gradient: %s" % g
        #o = sorted(self.order, key = lambda m: random.random())
        #num = 10
        #while num < len(o):
        #    g_partial = self.learner.gradient(self.X, self.w, o[0:num])
        #    print "Number of samples: %d" % num
        #    print "Partial Gradient: %s" % self.normalize(g_partial)
        #    num *= 2
    
    def gd(self):
        g = self.learner.gradient(self.X, self.w, self.order)
        g = self.normalize(g)
        print "Gradient: %s" % g

        a = self.learner.line_search(self.X, self.w, self.order, g)
        #a = 1.0
        #while a > 1e-5:
        #    print "Current alpha: %.7f" % a 
        #    tmp_w = []
        #    for i in range(len(self.w)):
        #        tmp_w.append(self.w[i] - a * g[i])
        #    old_w = self.w
        #    self.w = tmp_w
        #    print "Kendall %.7f" % self.evaluate()
        #    self.w = old_w
        #    a /= 2

        new_w = []
        for i in range(len(self.w)):
            new_w.append(self.w[i] - a * g[i])
        self.w = new_w
        #self.w = self.normalize(new_w)
        #self.w = self.normalize_sum(new_w)
        new_obj = self.learner.objective(self.X, self.w, self.order)
        print "New objective %.3f" % new_obj
        print "New weights: %s" % self.w

        return {'alpha': a, 'new_obj': new_obj}

    def dictw(self):
        ret = {}
        for i in range(len(self.w)):
            ret[self.feature_name[i]] = self.w[i]
        return ret

    @snsapi_utils.report_time
    def train(self):
        print "---- init ----"
        print "Weights: %s" % self.w
        print "Kendall's coefficient: %.3f" % self.evaluate()
        last_obj = self.learner.objective(self.X, self.w, self.order)
        for i in range(0, 1):
            print "Round %d" % i
            print "Kendall's coefficient: %.3f" % self.evaluate()
            ret = self.gd()
            alpha = ret['alpha']
            new_obj = ret['new_obj']
            if alpha < 1.0 / len(self.X) or float(last_obj - new_obj) / last_obj < 1e-4:
                # Termination criterion
                #    1. Step size too small, we are in the unstable region. 
                #    2. relative improvement in objective is too small. 
                break
            last_obj = new_obj
        print "Training terminated!"
        return self.dictw()

    def evaluate(self):
        ranked = sorted(self.samples.values(), key = lambda m: self._weight_feature(m), reverse = True)
        ret = evaluate_kendall([m.msg_id for m in ranked], order)
        return ret

    def init_weight_kendall(self, feature_name, samples, order):
        iw = {}
        for f in feature_name:
            print "Feature: %s" % f
            k = evaluate_kendall(sorted(samples.keys(), key = lambda m: samples[m].feature[f], reverse = True), order)
            iw[f] = k
        print "Init weight by Kendall: %s" % iw
        return iw


if __name__ == '__main__':
    import time
    begin = time.time()
    data = Serialize.loads(open('samples.pickle').read())
    samples = data['samples']
    order = data['order']
    end = time.time()
    print "Load finish. Time elapsed: %.3f" % (end - begin)

    try:
        iweight = json.loads(open('weights.json', 'r').read())
    except:
        iweight = None
    aw = AutoWeight(samples, order, iweight, LearnerSigmoid())

    ret = aw.sgd()

    #ret = aw.train()
    open('weights.json', 'w').write(str(snsapi_utils.JsonDict(ret)))

    #aw = AutoWeight(samples, order, {
    #    "contain_link": 0.0078408868790964727,
    #    "test": -0.010018632810608647,
    #    "text_len": 0.022876906485363457,
    #    "text_orig_len": 0.013349336089729578,
    #    "topic_interesting": -0.014742666918673125,
    #    "topic_news": 0.26628657037192432,
    #    "topic_nonsense": -0.5638193540760924,
    #    "topic_tech": 0.88305683823732894
    #}, LearnerSigmoid())

    #aw = AutoWeight(samples, order, {
    #    "contain_link": 1, 
    #    "test": 1, 
    #    "text_len": 1, 
    #    "text_orig_len": 1, 
    #    "topic_interesting": 1, 
    #    "topic_news": 1, 
    #    "topic_nonsense": 1, 
    #    "topic_tech": 1
    #}, LearnerSigmoid())

    # A better manual weight under current feature configuration
    #In [17]: aw.w = [0.01,-1,1,0,1,0.01,0,0]
    #In [18]: aw.evaluate()
    #total:168095; conc:134586; disc:33509
    #Out[18]: 0.6013087837234897


    #aw = AutoWeight(samples, order, \
    #        init_weight_kendall(\
    #        ["contain_link", "test", "text_len", "text_orig_len", \
    #        "topic_interesting", "topic_news", "topic_nonsense", "topic_tech"], \
    #        samples, order)\
    #        , LearnerSigmoid())

    #aw = AutoWeight(samples, order, {
    #    "contain_link": 1.00000, 
    #    "test": 1.00000, 
    #    "text_len": 0, 
    #    "text_orig_len": 0.01, 
    #    "topic_interesting": 30, 
    #    "topic_news": 30, 
    #    "topic_nonsense": -100, 
    #    "topic_tech": 500
    #}, LearnerSigmoid())

    #aw = AutoWeight(samples, order, {
    #    "contain_link": 1.00000, 
    #    "test": 1.00000, 
    #    "text_len": 0, 
    #    "text_orig_len": 0.01, 
    #    "topic_interesting": 30, 
    #    "topic_news": 30, 
    #    "topic_nonsense": -100, 
    #    "topic_tech": 500
    #}, LearnerSquareSigmoid())

    #aw.train()

    #ranked = sorted(samples.values(), key = lambda m: random.random())
    #ranked = sorted(samples.values(), key = lambda m: m.parsed.time)
    #ranked = sorted(samples.values(), key = lambda m: aw._weight_feature(m), reverse = True)
    #ret = evaluate_kendall([m.msg_id for m in ranked], order)
    #print ret
