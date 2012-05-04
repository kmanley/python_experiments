"""
Conclusion: time.clock() is about 30% slower than time.time() but has much finer resolution
test_time: 1329.04843 msecs
test_clock: 1747.95871 msecs
1325604420.6 1325604420.6 0.0
3.07821352607 3.07821411107 5.84999999997e-07
test_clock: min=1747.95871 msec, max=1747.95871 msec, avg=1747.95871 msec, numcalls=1
test_time: min=1329.04843 msec, max=1329.04843 msec, avg=1329.04843 msec, numcalls=1
"""

import time
from bw.util.decorators import timed

ITERS = 10000000

@timed
def test_time():
  for i in range(ITERS):
    time.time()

@timed
def test_clock():
  for i in range(ITERS):
    time.clock()


test_time()
test_clock()


x1 = time.time()
x2 = time.time()

print x1, x2, x2-x1

x1 = time.clock()
x2 = time.clock()

print x1, x2, x2-x1
