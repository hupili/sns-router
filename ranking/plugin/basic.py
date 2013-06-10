# -*- coding: utf-8 -*-

# This module contains basic features. 
# Feature extractors here are supposed to run with minimum configuration. 
# After running it well, users can enable more features. 

from base import FeatureBase
from ..feature import url_extract
from ..feature import user_extract
from ..feature import logger
from ..feature import json

import re
import random

class FeatureLength(FeatureBase):
    def __init__(self, env):
        super(FeatureLength, self).__init__(env)

        self.schema = {
                "text_len": "numeric",
                "text_orig_len": "numeric",
                "text_len_clean": "numeric",
                }

        self.face = []
        self.add_face_icons(self.env['dir_kdb'] + '/face.SinaWeiboStatus')
        self.add_face_icons(self.env['dir_kdb'] + '/face.RenrenStatus')

    def add_face_icons(self, fn_face):
        with open(fn_face, 'r') as fp:
            for f in fp.read().split('\n'):
                self.face.append(f.decode('utf-8'))

    def _clean(self, text):
        ct = text.encode('utf-8')
        ct = url_extract(ct)['text']
        #print ct
        ct = user_extract(ct)['text']
        #print ct
        ct = ct.decode('utf-8')
        for f in self.face:
            ct = ct.replace(f, '')
        #print ct
        _STOPWORD = u"的了是在有而以但一我你他它个啊这…、，！。：【】；（）“”《》\";,./1234567890(): ~|/·"
        for w in _STOPWORD:
            ct = ct.replace(w, '')
        #print ct
        return ct


    def add_features(self, msg):
        # Literal length
        msg.feature['text_len'] = len(msg.parsed.text)
        if 'text_orig' in msg.parsed:
            msg.feature['text_orig_len'] = len(msg.parsed.text_orig)
        else:
            msg.feature['text_orig_len'] = 0

        # Normalize
        max_text_len = 400.0
        max_text_orig_len = 250.0
        if msg.feature['text_len'] > max_text_len:
            msg.feature['text_len'] = max_text_len
        if msg.feature['text_orig_len'] > max_text_orig_len:
            msg.feature['text_orig_len'] = max_text_orig_len
        msg.feature['text_len'] /= max_text_len
        msg.feature['text_orig_len'] /= max_text_orig_len

        # Clean length
        max_text_len_clean = 400.0
        text_clean = self._clean(msg.parsed.text)
        msg.feature['text_len_clean'] = len(text_clean)
        if msg.feature['text_len_clean'] > max_text_len_clean:
            msg.feature['text_len_clean'] = max_text_len_clean
        msg.feature['text_len_clean'] /= max_text_len_clean

class FeatureEcho(FeatureBase):
    def __init__(self, env):
        super(FeatureEcho, self).__init__(env)

        fn_channel = self.env['dir_conf'] + '/channel.json'
        self.schema = {"echo": "numeric"}

        self.username = []
        fields = ["user_name", "username", "address"]    
        with open(fn_channel) as fp:
            for ch in json.loads(fp.read()):
                for f in fields:
                    if f in ch:
                        self.username.append(ch[f])

    def add_features(self, msg):
        for un in self.username:
            if msg.parsed['username'].count(un):
                msg.feature['echo'] = 1.0
                return
        msg.feature['echo'] = 0.0
        return

class FeatureLink(FeatureBase):
    """docstring for FeatureLink"""
    def __init__(self, env):
        super(FeatureLink, self).__init__(env)
        self.schema = {
                "contain_link": "{0,1}"
                }
        
    def add_features(self, msg):
        r = re.compile(r'https?://')
        if r.search(msg.parsed.text):
            msg.feature['contain_link'] = 1
        else:
            msg.feature['contain_link'] = 0 

class FeatureNoise(FeatureBase):
    """docstring for FeatureNoise"""
    def __init__(self, env):
        super(FeatureNoise, self).__init__(env)
        self.schema = {
                "noise": "numeric"
                }

    def add_features(self, msg):
        msg.feature['noise'] = random.random()

logger.debug('Feature module "basic" is plugged!')
