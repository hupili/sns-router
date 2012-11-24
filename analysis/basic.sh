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

exit 0 
