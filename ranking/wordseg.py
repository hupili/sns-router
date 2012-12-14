# -*- coding: utf-8 -*-

# https://github.com/pluskid/pymmseg-cpp/
import mmseg

# The way shown in README file. Does not work. 
#mmseg.dict_load_words('kdb/mmseg_words.dic')
#mmseg.dict_load_chars('kdb/mmseg_chars.dic')

# Read from code
tp_dict =  mmseg.Dictionary.dictionaries
#mmseg.Dictionary.dictionaries = (tp_dict[0], ('words', 'kdb/mmseg_words.dic'))
# Use Sogo dict only
#mmseg.Dictionary.dictionaries = (tp_dict[0], ('words', 'kdb/Freq/SogouLabDic.dic.utf-8.pymmseg-format'))
# Use Sogo + pymmseg dict merged version
mmseg.Dictionary.dictionaries = (tp_dict[0], ('words', 'kdb/words.merged.dic'))
mmseg.Dictionary.load_dictionaries()

# ？ is not included. Question mark is a strong symbol 
# of the type of message. We keep it for future use.  
_STOPWORD = u"的了是在有而以但一我你他它个啊这…、，！。：【】；（）“”《》\";,./1234567890(): ~|/·"
STOPWORD = {}
for sw in _STOPWORD:
    STOPWORD[sw] = 1

def wordseg(text):
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    algor = mmseg.Algorithm(text)
    return list(algor)

def wordseg_clean(text):
    from userext import user_extract
    from urlext import url_extract

    if isinstance(text, unicode):
        text = text.encode('utf-8')
    
    t = url_extract(text)
    t = user_extract(t['text'])

    l = wordseg(t['text'])
    ret = []
    for w in l:
        if not w.text.decode('utf-8') in STOPWORD:
            ret.append(w)

    return ret

if __name__ == '__main__':
    while (True):
        try:
            text = raw_input()
            # Test piece:
            # print "text:"
            # print text
            # print "wordseg:"
            # print " ".join([t.text for t in wordseg(text)])
            # print "wordseg_clean:"
            # print " ".join([t.text for t in wordseg_clean(text)])
            for tok in wordseg_clean(text):
                print '%s' % tok.text
        except EOFError:
            break

# Quick test of this script
# sed -n '3p' data/text.SinaWeiboStatus | python wordseg.py
