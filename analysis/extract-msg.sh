#!/bin/bash
#
#only run for the latest week
#

# octave:1> 60 * 60 * 24 * 7
# ans =  604800

cur_time=`date +%s`
msg_time=`expr $cur_time - 604800`
echo "cur time: $cur_time"
echo "msg time: $msg_time"

mkdir -p data

sql="sqlite3 srfe.db"

$sql "select time,username from msg where time > $msg_time" > data/msg

cd data

cat msg | tr '|' '\t' > msg.tab 

cut -f1 msg.tab | xargs -i date -d@'{}' +'%Y%m%d	%H' > msg.tab.time
cut -f1 msg.tab.time | sort | uniq -c > msg.tab.time.day-freq
cut -f2 msg.tab.time | sort | uniq -c > msg.tab.time.hour-freq

cut -f2 msg.tab > msg.tab.username
cat msg.tab.username | sort | uniq -c > msg.tab.username.freq
sort -nr msg.tab.username.freq > msg.tab.username.freq.sortnr

cd -

exit 0 
