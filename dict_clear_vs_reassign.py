"""
conclusion: the exception adds a lot of overhead
test_1: 425.79476 msecs
test_2: 3.02328 msecs
"""
import sys
import time
from decorators import timed
import ujson
import copy
import cPickle as pickle
import marshal

ITERS = range(1000)

D = {x: str(x) for x in range(10)}

@timed
def test_1():
    for i in ITERS:
        d = D.copy()
        d.clear()

@timed
def test_2():
    for i in ITERS:
        d = D.copy()
        d = {}

test_1()
test_2()
