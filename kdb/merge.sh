#!/bin/bash

export LC_ALL="C"
sed 's/^[0-9]* //g' Freq/SogouLabDic.dic.utf-8.pymmseg-format | sort > Freq/SogouLabDic.dic.utf-8.pymmseg-format.word-sort
sed 's/^[0-9]* //g' words.dic | sort > words.dic.word-sort
join -v1 words.dic.word-sort Freq/SogouLabDic.dic.utf-8.pymmseg-format.word-sort > words.dic.more
awk '{printf("1 %s\n", $0)}' words.dic.more | cat Freq/SogouLabDic.dic.utf-8.pymmseg-format - > words.merged.dic

#Some stat. Merge Sogo and pymmseg dict. 
#
# $wc -l Freq/SogouLabDic.dic
# 157202 Freq/SogouLabDic.dic
# $wc -l Freq/SogouLabDic.dic.utf-8.pymmseg-format
# 134792 Freq/SogouLabDic.dic.utf-8.pymmseg-format
# $wc -l words.dic
# 120308 words.dic
# $wc -l words.dic.more 
# 55480 words.dic.more
# $wc -l words.merged.dict 
# 190272 words.merged.dict
