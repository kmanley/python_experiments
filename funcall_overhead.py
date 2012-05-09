"""
conclusion: it's worth inlining for performance
test_1: 10.11723 msecs
test_2: 2.44628 msecs
"""
import sys
import time
from decorators import timed
import ujson
import copy
import cPickle as pickle
import marshal

ITERS = range(1)

def nop():
    pass

@timed
def test1():
    for i in ITERS:
        pass

@timed
def test2():
    for i in ITERS:
        nop()

test1()
test2()
