# -*- coding: utf-8 -*-

#from base import FeatureBase
#from urlext import url_extract
#from userext import user_extract

from base import FeatureBase
from ..feature import url_extract
from ..feature import user_extract
from ..feature import logger

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
        #_STOPWORD = u"的了是在有而以但一我你他它个啊这…、，！。：【】；（）“”《》\";,./1234567890"
        from wordseg import _STOPWORD
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

logger.debug('Feature module "length" is plugged!')
