"""
conclusion:
it pays to rebind. Strangely, the generic rebind is slow though...wtf?

test_1: 18.72417 msecs
test_2: 8.98122 msecs
test_3: 20.86273 msecs
"""
import sys
import time
from bw.util.decorators import timed
import ujson
import copy
import cPickle as pickle
import marshal

ITERS = range(10000000)
import globals
LISTAPPEND = globals.LIST.append

GENERICLISTAPPEND = list.append

@timed
def test_1():
    for i in ITERS:
        globals.LIST.append(i)

@timed
def test_2():
    for i in ITERS:
        LISTAPPEND(i)

@timed
def test_3():
    L = globals.LIST
    for i in ITERS:
        GENERICLISTAPPEND(L, i)

import globals2
from globals2 import nop
mynop = globals2.nop

@timed
def test_4():
    for i in ITERS:
        nop()

@timed
def test_5():
    for i in ITERS:
        mynop()

thistxid = 0

@timed
def test_6():
    for i in ITERS:
        mynop()


@timed
def test_7():
    for i in ITERS:
        mynop()



test_1()
test_2()
test_3()
test_4()
test_5()