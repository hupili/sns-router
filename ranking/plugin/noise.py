# -*- coding: utf-8 -*-

#from base import FeatureBase
#from urlext import url_extract
#from userext import user_extract

from base import FeatureBase
from ..feature import url_extract
from ..feature import user_extract
from ..feature import logger
import random

class FeatureNoise(FeatureBase):
    """docstring for FeatureNoise"""
    def __init__(self, env):
        super(FeatureNoise, self).__init__(env)
        self.schema = {
                "noise": "numeric"
                }

    def add_features(self, msg):
        msg.feature['noise'] = random.random()

logger.debug('Feature module "noise" is plugged!')
