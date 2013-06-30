import sys
sys.path.append('bottle')
sys.path.append('snsapi')
import snsapi
from snsapi.utils import report_time

from queue import *

sp = SNSPocket()
q = SRFEQueue(sp)
q.connect()
q.refresh_tags()


@report_time
def output():
    ml = q.output()

output()

# Test DB: my DB from Nov 2012 to June 2013
# Size: ~3.1 GB before index; ~3.1 GB after index
#
# Before index: 12.33, 12.12, 12.15
# After index: 0.04

@report_time
def output_more():
    ml = q.output(count=500)

output_more()

# output_more: 0.62
