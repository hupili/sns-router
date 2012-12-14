#!/bin/bash

# Download from:
#     http://www.sogou.com/labs/dl/w.html

tar -xzvf SogouW.tar.gz
cd Freq 
iconv -f gbk -t utf-8 SogouLabDic.dic > SogouLabDic.dic.utf-8
cat SogouLabDic.dic.utf-8 | awk '{printf("%d %s\n",$2,$1)}' > SogouLabDic.dic.utf-8.pymmseg-format
cd -

exit 0 
