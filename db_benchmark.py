import sys
sys.path.append('bottle')
sys.path.append('snsapi')
import snsapi
from snsapi.utils import report_time

from queue import *

test_digest = ["cd0a7372ac5025608e2625c267e270bfc943578a",
"28cab30bd5815623a7a7dcf45195bea2780a8dd1",
"e467b49b1a1e211440ef45eb6dbf35c18cbff787",
"7b0888b927ff3d36e8a2e1249cca00085897dff4",
"e0700e78f7fea87078b3acd095c958ac66515dc4",
"ee100f15c0b18707afb00282428949ff009aeead",
"8dd80be3026d399075bb6afe53cbf2b3d9bd48f8",
"5dd3fe283d7d6db4ea945b535b358df9afa73f52",
"97a9f822543053ae2f9e1ec61f418805fcfb3811",
"77b63a02ded5442e1f37406b23e912f2383f0cb5"]

sp = SNSPocket()
q = SRFEQueue(sp)
q.connect()
q.refresh_tags()

def search_digest(digest):
    cur = q.con.cursor()
    r = cur.execute('''
    SELECT digest FROM msg
    WHERE digest = ?
    ''', (digest, ))

@report_time
def search_digest_all():
    for d in test_digest:
        search_digest(d)

search_digest_all()

# Test DB: my DB from Nov 2012 to June 2013
# Size: ~2.5 GB before index; 3.0 GB after index
#
# Before creating index: 7.19, 7.41, 7.37
# After creating index: 0.00


@report_time
def search_digest_all2():
    for i in xrange(10000):
        for d in test_digest:
            search_digest(d)

search_digest_all2()

# After creating index: 2.47

@report_time
def search_digest_non_exists():
    non_exists = ["e467b49b111e201440ef45eb6dbf35d18cbff787",
    "188ab30bd5815623a7a7dcfc5195bea2780a8dd1"]
    for i in xrange(10000):
        for d in non_exists:
            search_digest(d)

search_digest_non_exists()

# After creating index: 0.45
