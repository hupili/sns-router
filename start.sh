#!/bin/bash

nohup sh -c 'python srfe.py 2>&1 | tee -a srfe.log' &
