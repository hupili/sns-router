#!/bin/bash
#Dump text files for word segmentation

mkdir -p data

sql="sqlite3 srfe.db"

$sql "select text from msg where platform='SinaWeiboStatus'" > data/text.SinaWeiboStatus
$sql "select text from msg where platform='RenrenStatus'" > data/text.RenrenStatus
$sql "select text from msg where platform='TencentWeiboStatus'" > data/text.TencentWeiboStatus
$sql "select text from msg" > data/text.all

cd data
#cat text.SinaWeiboStatus text.RenrenStatus text.TencentWeiboStatus > text.all
cd -

exit 0 
