# -*- coding: utf-8 -*-

# This module contains basic features. 
# Feature extractors here are supposed to run with minimum configuration. 
# After running it well, users can enable more features. 

from base import FeatureBase

import re
import random

class FeatureHasPic(FeatureBase):
    def __init__(self, env):
        super(FeatureHasPic, self).__init__(env)

        self.schema = {
                "has_pic": "numeric"
                }

    def add_features(self, msg):
        msg.feature['has_pic'] = int('picture' in [a['type'] for a in msg.parsed.attachments])
