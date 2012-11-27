#!/bin/bash

sql="sqlite3 srfe.db"

echo "total number of messages:"
$sql 'select count(*) from msg'
echo "number of seen messages:"
$sql 'select count(*) from msg where flag="seen";'
echo "number of tag-messages:"
$sql 'select count(*) from msg_tag;'
echo "number of logs:"
$sql 'select count(*) from log;'
echo "number of forwards:"
$sql 'select count(*) from log where operation like "%forward%";'
echo "number different tags:"
$sql 'select name,count(*) from msg_tag,tag where tag_id = tag.id group by tag_id;'

tm="tag_mapping.json"
echo "saving tag mapping to '$tm'"
echo "{" > $tm
$sql 'select name,id from tag;' | tr '|' ' ' | awk '{printf("\"%s\": %d,\n", $1, $2)}' >> $tm
# Just to fit in json format...
echo "\"__fake__\": 99999" >> $tm
echo "}" >> $tm


exit 0 
