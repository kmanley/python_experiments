"""
Conclusion:

Data size
   100
  1000
 10000
100000


"""
import sys
import time
from decorators import timed
import binascii, base64
import ujson
import copy
import cPickle
import marshal

ITERS = range(1000)

DATA = [x for x in range(10000)]
print "data len: %s" % len(DATA)

@timed
def test_0():
    for i in ITERS:
        x = cPickle.dumps(DATA, protocol=0) # ascii

@timed
def test_1():
    for i in ITERS:
        x = cPickle.dumps(DATA, protocol=1) # original bin

@timed
def test_2():
    for i in ITERS:
        x = cPickle.dumps(DATA, protocol=2) # latest bin

@timed
def test_3():
    for i in ITERS:
        x = binascii.hexlify(cPickle.dumps(DATA, protocol=2)) # latest bin

test_0()
test_1()
test_2()
test_3()

