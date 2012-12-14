# -*- coding: utf-8 -*-

# This module contains basic features. 
# Feature extractors here are supposed to run with minimum configuration. 
# After running it well, users can enable more features. 

from base import FeatureBase
from ..feature import url_extract
from ..feature import user_extract
from ..feature import logger
from ..feature import Serialize

class FeatureUser(FeatureBase):
    """docstring for FeatureTopic"""
    def __init__(self, env):
        super(FeatureUser, self).__init__(env)
        self.schema = {
                "user_tech": "numeric",
                "user_news": "numeric",
                "user_interesting": "numeric",
                "user_nonsense": "numeric",
                }

        # User dict
        fn_udict = self.env['dir_kdb'] + "/udict.pickle"
        self.udict = Serialize.loads(open(fn_udict).read())

    def _user(self, dct, msg):
        if msg.parsed.username in dct:
            return dct[msg.parsed.username]
        else:
            return 0

    def add_features(self, msg):
        msg.feature['user_tech'] = self._user(self.udict['tech'], msg)
        msg.feature['user_news'] = self._user(self.udict['news'], msg)
        msg.feature['user_interesting'] = self._user(self.udict['interesting'], msg)
        msg.feature['user_nonsense'] = self._user(self.udict['nonsense'], msg)

logger.debug('Feature module "length" is plugged!')
