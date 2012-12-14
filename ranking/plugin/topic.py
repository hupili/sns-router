# -*- coding: utf-8 -*-

#from base import FeatureBase
#from urlext import url_extract
#from userext import user_extract

from base import FeatureBase
from ..feature import url_extract
from ..feature import user_extract
from ..feature import wordseg_clean
from ..feature import logger
from ..feature import Serialize
import random

class FeatureTopic(FeatureBase):
    """docstring for FeatureTopic"""
    def __init__(self, env):
        super(FeatureTopic, self).__init__(env)
        self.schema = {
                "topic_tech": "numeric",
                "topic_news": "numeric",
                "topic_interesting": "numeric",
                "topic_nonsense": "numeric",
                }

        # Topic dict
        fn_tdict = self.env['dir_kdb'] + "/tdict.pickle"
        self.tdict = Serialize.loads(open(fn_tdict).read())

    def _topic(self, dct, msg):
        score = 0.0
        terms = wordseg_clean(msg.parsed.text)
        for t in terms:
            if t.text in dct:
                score += dct[t.text]
        return score

    def add_features(self, msg):
        msg.feature['topic_tech'] = self._topic(self.tdict['tech'], msg)
        msg.feature['topic_news'] = self._topic(self.tdict['news'], msg)
        msg.feature['topic_interesting'] = self._topic(self.tdict['interesting'], msg)
        msg.feature['topic_nonsense'] = self._topic(self.tdict['nonsense'], msg)
        
        msg.feature['topic_interesting'] /= 0.08772
        msg.feature['topic_nonsense'] /= 0.25152
        msg.feature['topic_tech'] /= 0.04399
        msg.feature['topic_news'] /= 0.37376
logger.debug('Feature module "noise" is plugged!')
