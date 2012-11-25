# -*- coding: utf-8 -*-

# https://github.com/pluskid/pymmseg-cpp/
import mmseg
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
