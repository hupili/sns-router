#!/bin/bash

mkdir -p kdb

cat data/text.RenrenStatus | python wordseg.py  | sort | uniq -c | sort -nr > kdb/term.RenrenStatus
cat data/text.SinaWeiboStatus | python wordseg.py  | sort | uniq -c | sort -nr > kdb/term.SinaWeiboStatus
cat data/text.TencentWeiboStatus | python wordseg.py  | sort | uniq -c | sort -nr > kdb/term.TencentWeiboStatus

cat data/text.all | python wordseg.py  | sort | uniq -c | sort -nr > kdb/term.all

exit 0 
