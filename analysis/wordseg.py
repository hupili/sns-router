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

def wordseg(text):
    algor = mmseg.Algorithm(text)
    return list(algor)

if __name__ == '__main__':
    while (True):
        try:
            text = raw_input()
            for tok in wordseg(text):
                print '%s' % tok.text
        except EOFError:
            break

# Quick test of this script
# sed -n '3p' data/text.SinaWeiboStatus | python wordseg.py
