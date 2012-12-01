#!/bin/bash
#
# Extract tags for user statistics

mkdir -p data

sql="sqlite3 srfe.db"

$sql 'select * from tag' > data/tag.schema

for ((tag_id=1;tag_id<=9;tag_id++))
do
	$sql "select username from msg,msg_tag where msg_id=msg.id and tag_id=$tag_id" > data/tag.id$tag_id
	cd data
	sort tag.id$tag_id | uniq -c | sort -nr > tag.id$tag_id.freq
	cd -
done

exit 0 
