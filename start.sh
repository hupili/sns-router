#!/bin/bash

nohup python srfe.py 2>&1 >> srfe.log &
PID=$!
echo $PID > srfe.pid

exit 0
