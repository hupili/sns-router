# -*- coding: utf-8 -*-

from ..feature import logger

class FeatureBase(object):
    """
    Base class for features
    
    """
    def __init__(self, env):
        '''
        env: Environment variables

        '''
        super(FeatureBase, self).__init__()
        self.env = env
        # If one want the feature able to export into Weka's arff format, 
        # the schema field is essential. It is a valid arff attribute 
        # definition string, e.g.: (only inside quotes)
        #    * "numeric"
        #    * "{no, yes}"
        # To enable auto training by 'autoweight.py' script, features are 
        # required to be "numeric". However, there may be some use cases 
        # for nominal values which is represented in numeric form. e.g. the
        # 'contain_link' feature takes either 0 or 1. As long as the appearance
        # is "0" or "1", our script can process it. If you want to incorporate
        # more information into arff exports, you can use "{0, 1}", insead of
        # "numeric". We'll set the default to be "numeric".
        self.schema = {"feature": "numeric"}

    def add_features(self, msg):
        '''
        Add features to msg object. 

        msg: snsapi.snstype.Message object

        '''
        msg.feature['feature'] = 1.0

logger.debug('Feature module "length" is plugged!')

