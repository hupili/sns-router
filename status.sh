#!/bin/bash

for pid in `cat srfe.pid`
do
	ps aux | grep srfe.py | grep $pid
done

