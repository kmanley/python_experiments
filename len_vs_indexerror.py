"""
Test when item exists
--------------------------------------
test_len: 135.55775 msecs
test_indexerror: 67.87821 msecs

Test when item does not exist
--------------------------------------
test_len: 93.04872 msecs
test_indexerror: 847.24317 msecs

Conclusion: if you are pretty sure item is there, then use try/except IndexError
Otherwise, test length

"""
#import sys
#import time
#import ujson
#import copy
#import cPickle as pickle
#import marshal
import timeit

#ITERS = range(1000000)

LST = []#[1]

#@timed
def test_len():
    if len(LST) > 0:
        x = LST[0]
    else:
        x = None

#@timed
def test_indexerror():
    try:
        x = LST[0]
    except IndexError:
        x = None


print timeit.timeit("test_len()", "from __main__ import test_len")
print timeit.timeit("test_indexerror()", "from __main__ import test_indexerror")
#test_len()
#test_indexerror()

