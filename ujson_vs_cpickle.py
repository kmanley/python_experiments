"""
Conclusion: marshal is fastest, cpickle is about as fast as ujson as long as you use protocol=-1
Not everything can be marshalled

"""
import sys
import time
from decorators import timed
import ujson
import copy
import cPickle as pickle
import marshal

ITERS = range(100)

deepcopy = copy.deepcopy
ujson_dumps = ujson.dumps
marshal_dumps = marshal.dumps
pickle_dumps = pickle.dumps

@timed
def test_copy():
    for i in ITERS:
        unused = deepcopy(DATA)

@timed
def test_ujson():
    for i in ITERS:
        unused = ujson_dumps(DATA)

@timed
def test_cpickle():
    for i in ITERS:
        unused = pickle_dumps(DATA, protocol=-1) # IMPORTANT, highest protocol is the fastest

@timed
def test_marshal():
    for i in ITERS:
        unused = marshal_dumps(DATA)


#DATA = {"fooooooooooooooo" : [1,2,3,100,200, {"bar":"wot?!?"}, (100,200,300), "this is a string blah blah blah ", 1.0],
#        2093802802 : "sljsdfjlsdf ljsdf ljsdf jlsdf jlsdf jlsdf",
#        "bazzazazazaz" : range(10000)}
#print DATA
#DATA = "abc" * 100
#print "data size: %s" % len(ujson.dumps(DATA))

for dtype, func in (("string", lambda size : "X" * size),
                    ("dict", lambda size : {"key%s" % i: i for i in range(size)}),
                    ("tuple", lambda size : (1,) * size),
                    ("list", lambda size : [1,] * size)):
    for size in (10, 100, 1000, 10000, 100000):
        print "%s of size %s" % (dtype, size)
        DATA = func(size)
        print "data size sanity check: %d" % len(pickle.dumps(DATA, protocol=-1))
        test_copy()
        test_ujson()
        test_cpickle()
        test_marshal()
        print "-" * 80


