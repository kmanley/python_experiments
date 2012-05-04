"""
conclusion: the exception adds a lot of overhead
test_1: 425.79476 msecs
test_2: 3.02328 msecs
"""
import sys
import time
from bw.util.decorators import timed
import ujson
import copy
import cPickle as pickle
import marshal

ITERS = range(1000)

DATA = [x for x in range(10)]
DATA.append(DATA)

#COPYFUNCS =

@timed
def test_1():
    for i in ITERS:
        try:
            marshal.dumps(DATA)
        except ValueError:
            pickle.dumps(DATA)

@timed
def test_2():
    for i in ITERS:
        pickle.dumps(DATA)


test_1()
test_2()
