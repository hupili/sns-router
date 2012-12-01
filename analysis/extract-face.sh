#!/bin/bash
# Extract face icons for further cleanup messages

mkdir -p kdb

# Sina, it's easy
# 1. "[xxx]"
# 2. Ignore those discussing programming, e.g. [i], [i - 3], ...
cat data/text.SinaWeiboStatus | grep -oP '\[.{2,10}?\]' | grep -vP "[,+-\./=%^*@]" | sort | uniq > kdb/face.SinaWeiboStatus

# Tencent!
# Damn this guy who choose to use "/xxxx"
#
# http://unix.stackexchange.com/questions/6516/filtering-invalid-utf8

#cat data/text.TencentWeiboStatus | grep -oP '\/[^/0-9a-zA-Z @|+-_()*&\^%$#[:print:]]{2,8}' | sort | uniq | wc -l 

#cat data/text.TencentWeiboStatus | grep -oP '\/[^/0-9a-zA-Z @|+-_()*&\^%$#[:print:]]{2,8}' | sort | uniq | perl -l -ne '/
#^( ([\x00-\x7F])              # 1-byte pattern
#|([\xC2-\xDF][\x80-\xBF])   # 2-byte pattern
#|((([\xE0][\xA0-\xBF])|([\xED][\x80-\x9F])|([\xE1-\xEC\xEE-\xEF][\x80-\xBF]))([\x80-\xBF])) # 3-byte pattern
#|((([\xF0][\x90-\xBF])|([\xF1-\xF3][\x80-\xBF])|([\xF4][\x80-\x8F]))([\x80-\xBF]{2}))       # 4-byte pattern
#)*$ /x or print' | sort | uniq > kdb/face.TencentWeiboStatus

# Renren
# 1. Ignore those @xxx pattern, "@xxx(11111)"
# 2. "(xxx)"
cat data/text.RenrenStatus | grep -vP '@.+?\(\d+\)' | grep -oP '\(.{2,10}?\)' | grep -vP "[,+-\./=%^*@]" | sort | uniq > kdb/face.RenrenStatus

exit 0 
