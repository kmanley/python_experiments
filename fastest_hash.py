"""
Conclusion: ujson is faster
"""
import sys
import time
from decorators import timed
import ujson
import cPickle as pickle

from hashlib import md5, sha1, sha224, sha256, sha384, sha512

ITERS = 1000

DATA = {"fooooooooooooooo" : [1,2,3,100,200, {"bar":"wot?!?"}, (100,200,300), "this is a string blah blah blah ", 1.0],
        2093802802 : "sljsdfjlsdf ljsdf ljsdf jlsdf jlsdf jlsdf",
        "bazzazazazaz" : range(10000)}

print "data size: %s" % len(ujson.dumps(DATA))

@timed
def test_md5():
    for i in range(ITERS):
        x = md5(repr(DATA)).hexdigest()

@timed
def test_sha1():
    for i in range(ITERS):
        x = sha1(repr(DATA)).hexdigest()


test_md5()
test_sha1()

