#!/bin/bash

#for pid in `ps aux | grep srfe.py | awk '{print $2}'`
for pid in `cat srfe.pid`
do
	kill $pid
done

exit 0
