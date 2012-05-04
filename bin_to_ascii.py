"""
Conclusion: hexlify is faster

data len: 2752
test_1: 9.02761 msecs  # hexlify is very fast
test_2: 192.23747 msecs  # repr is slower than I expected
test_3: 45.51123 msecs # base64 is slow
test_4: 228.06894 msecs # zlib is very slow

"""
import sys
import time
from bw.util.decorators import timed
import binascii, base64
import ujson
import copy
import cPickle as pickle
import marshal
import zlib

ITERS = range(1000)

DATA = pickle.dumps([x for x in range(1000)], protocol=-1)
print "data len: %s" % len(DATA)

@timed
def test_1():
    for i in ITERS:
        x = binascii.hexlify(DATA)
    #print "hexlify: %s" % x

@timed
def test_2():
    for i in ITERS:
        x = repr(DATA)
    #print "hexlify: %s" % x


@timed
def test_3():
    for i in ITERS:
        x = base64.encodestring(DATA)
    #print "base64: %s" % x

@timed
def test_4():
    for i in ITERS:
        x = binascii.hexlify(zlib.compress(DATA))
    #print "rlecode_hqx: %s" % x


test_1()
test_2()
test_3()
test_4()

