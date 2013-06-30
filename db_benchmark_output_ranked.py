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
def output_ranked():
    ml = q.output_ranked(200, 86400)

output_ranked()

# Test DB: my DB from Nov 2012 to June 2013
# Size: ~3.1 GB before index; ~3.1 GB after index
#
# Before: 3.8, 3.9
# After: 0.45, 0.42

@report_time
def output_more_ranked():
    ml = q.output_ranked(2000, 86400)

output_more_ranked()

# Before: 2.51, 2.52
