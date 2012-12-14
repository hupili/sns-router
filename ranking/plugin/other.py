# -*- coding: utf-8 -*-

# This module contains basic features. 
# Feature extractors here are supposed to run with minimum configuration. 
# After running it well, users can enable more features. 

from base import FeatureBase
from ..feature import url_extract
from ..feature import user_extract
from ..feature import logger

class FeatureFace(FeatureBase):
    """docstring for FeatureBase"""
    def __init__(self, env):
        super(FeatureFace, self).__init__(env)
        self.schema = {
                "test": "numeric",
                }

    def add_features(self, msg):
        msg.feature['test'] = 1

logger.debug('Feature module "other" is plugged!')
