#!/bin/bash
#
# Start SRFE in the current console. 
#
# To run SRFE in the backend, 
# see 'start.sh', 'status.sh' and 'kill.sh'

python srfe.py 2>&1 | tee -a srfe.log
