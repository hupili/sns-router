#!/bin/bash

db="srfe_queue.db"
dir="archive"
datestr=`date +%Y%m%d-%H%M%S`
new_db="$dir/$db.$datestr"

echo "from: $db"
echo "to: $new_db"

mkdir -p $dir
cp $db $new_db

exit 0 
