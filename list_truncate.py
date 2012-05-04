"""
Conclusions: depends on size of list
10:
test_1: 33.18260 msecs
test_2: 48.01201 msecs

1000:
test_1: 937.97337 msecs
test_2: 873.38759 msecs



"""
import sys
import time
from bw.util.decorators import timed
import ujson
import cPickle as pickle

from hashlib import md5, sha1, sha224, sha256, sha384, sha512

ITERS = 1000

@timed
def test_1():
    for i in range(ITERS):
        L = range(10000)
        L = []

@timed
def test_2():
    for i in range(ITERS):
        L = range(10000)
        L.__imul__(0)


test_1()
test_2()