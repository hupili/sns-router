#!/bin/bash

for pid in `ps aux | grep srfe.py | awk '{print $2}'`
do
	kill $pid
done
