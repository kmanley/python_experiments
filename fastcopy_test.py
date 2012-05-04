"""
Conclusion: marshal is fastest, cpickle is about as fast as ujson as long as you use protocol=-1
Not everything can be marshalled

"""
import sys
import time
from bw.util.decorators import timed
import ujson
import copy
import cPickle as pickle
import marshal

ITERS = range(1)

deepcopy = copy.deepcopy
ujson_loads = ujson.loads
ujson_dumps = ujson.dumps
marshal_loads = marshal.loads
marshal_dumps = marshal.dumps
pickle_loads = pickle.loads
pickle_dumps = pickle.dumps

@timed
def test_copy():
    for i in ITERS:
        unused = deepcopy(DATA)
    #assert unused == DATA
    #assert id(unused) != id(DATA)

#@timed
#def test_ujson():
#    for i in ITERS:
#        unused = ujson_loads(ujson_dumps(DATA))
#    assert unused == DATA

@timed
def test_cpickle():
    for i in ITERS:
        unused = pickle_loads(pickle_dumps(DATA, protocol=-1)) # IMPORTANT, highest protocol is the fastest
    #assert unused == DATA
    #assert id(unused) != id(DATA)

@timed
def test_marshal():
    for i in ITERS:
        unused = marshal_loads(marshal_dumps(DATA))
    #assert unused == DATA
    assert id(unused) != id(DATA)

from bitarray import bitarray
from blist import blist, sortedlist, sorteddict, sortedset
from collections import deque
import numpy
from numpy import array, matrix
numpy_fromstring = numpy.fromstring

from fastcopy import fast_copy

#def identity(o):
#    return o
#
#def dopickle(o):
#    return pickle_loads(pickle_dumps(o, protocol=-1))
#
#def trymarshal(o):
#    try:
#        return marshal_loads(marshal_dumps(o))
#    except:
#        # marshal can fail if there is a cycle
#        return pickle_loads(pickle_dumps(o, protocol=-1))
#
#COPYFUNCS = {str : identity,
#             unicode : identity,
#             int : identity,
#             long: identity,
#             float: identity,
#             tuple : identity,
#             set: trymarshal,
#             list: trymarshal, # NOT o[::], as that is a shallow copy, only deepcopy for strings
#             dict: trymarshal,
#             # numpy types
#             array : deepcopy,
#             matrix : deepcopy,
#             # other 3rd party types
#             bitarray : deepcopy,
#             #blist : lambda o : o[::], NO: that's a shallow copy--use pickle
#             #sortedlist : lambda o : o[::], NO: that's a shallow copy--use pickle
#             # TODO: igraph, pandas
#             }

@timed
def test_universal():
    for i in ITERS:
        unused = fast_copy(DATA)
    #assert unused == DATA

#DATA = {"fooooooooooooooo" : [1,2,3,100,200, {"bar":"wot?!?"}, (100,200,300), "this is a string blah blah blah ", 1.0],
#        2093802802 : "sljsdfjlsdf ljsdf ljsdf jlsdf jlsdf jlsdf",
#        "bazzazazazaz" : range(10000)}
#print DATA
#DATA = "abc" * 100
#print "data size: %s" % len(ujson.dumps(DATA))

for dtype, func in (
    ("string", lambda size : "X" * size),
    ("unicode", lambda size : u"X" * size),
    ("bitarray", lambda size: bitarray(size)),
    ("numpyarray", lambda size : numpy.linspace(0, size, size)),
    ("numpymatrix", lambda size : numpy.matrix(numpy.linspace(0, size, size))),
    ("dict of string:int", lambda size : {"key%s" % i: i for i in range(size)}),
    ("list of int", lambda size : [1,] * size),
    ("list of string", lambda size : ["A",] * size),
    ("set", lambda size : set(range(size))),
    ("blist of int", lambda size : blist(range(size))),
    ("sortedlist of int", lambda size : sortedlist(range(size))),
    ("sortedset of int", lambda size : sortedset(range(size))),
    ("deque of int", lambda size : deque(range(size))),
    ):
    for size in (100, 1000, 10000, 100000):
        print "%s of size %s" % (dtype, size)
        DATA = func(size)
        sanity_len = len(pickle.dumps(DATA, protocol=-1))
        print "data size sanity check: %d" % sanity_len
        assert sanity_len >= size
        test_copy()
        #test_ujson()
        test_cpickle()
        try:
            marshal.dumps(DATA)
        except:
            print "can't marshal %s" % dtype
        else:
            test_marshal()
        test_universal()
        print "-" * 80


