#!/bin/bash

mkdir -p data

sql="sqlite3 srfe.db"

$sql 'select * from log where operation like "%[flag]%" or operation like "%[tag]%"' > data/log.flag
$sql 'select * from log where operation like "%[forward]%"' > data/log.forward

cd data

cat log.flag | tr '|' '\t' | tr ';' '\t' | cut -f2,4 > log.flag.tab
cut -f1 log.flag.tab > log.flag.tab.f1
cat log.flag.tab.f1 | xargs -i date -d@'{}' +'%Y%m%d	%H' > log.flag.tab.f1.time
cut -f1 log.flag.tab.f1.time | sort | uniq -c > log.flag.tab.f1.time.day-freq
cut -f2 log.flag.tab.f1.time | sort | uniq -c > log.flag.tab.f1.time.hour-freq

cat log.forward | tr '|' '\t' | tr ';' '\t' | cut -f2,3 | sed 's/\[forward\]//g' > log.forward.tab
cut -f1 log.forward.tab > log.forward.tab.f1

cd -

exit 0 
