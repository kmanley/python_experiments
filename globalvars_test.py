"""
Conclusions: referencing var from another module is surprisingly fast, faster than accessing class member in same module (WTF?)

test_global: 571.14142 msecs
test_local: 473.60028 msecs
test_g: 838.36489 msecs
test_g_rebound: 619.06256 msecs
test_othermod: 579.88177 msecs
test_othermod2: 932.52931 msecs
foo1: 808.95093 msecs
foo2: 733.44317 msecs


Also note: the global statement is not executed, it's only used at compile time

x1
              0 LOAD_GLOBAL              0 (GLOBAL)
              3 STORE_FAST               0 (x)
              6 LOAD_CONST               0 (None)
              9 RETURN_VALUE
---------------------------------------------------------------------
x2
              0 LOAD_GLOBAL              0 (GLOBAL)
              3 STORE_FAST               0 (x)
              6 LOAD_CONST               0 (None)
              9 RETURN_VALUE

"""
import sys
import time
from bw.util.decorators import timed
import ujson
import cPickle as pickle

from hashlib import md5, sha1, sha224, sha256, sha384, sha512

ITERS = 1 #000 #0000

GLOBAL = 100

#class g:
#    foo = 100

@timed
def test_global():
    global GLOBAL
    for i in range(ITERS):
        x = GLOBAL

@timed
def test_local():
    loc = GLOBAL
    for i in range(ITERS):
        x = loc

#@timed
#def test_g():
#    for i in range(ITERS):
#        x = g.foo

#from globalvars import x
#@timed
#def test_othermod():
#    for i in range(ITERS):
#        y = x

import globalvars
@timed
def test_othermod():
    for i in range(ITERS):
        y = globalvars.x

#g_foo = g.foo
#@timed
#def test_g_rebound():
#    global g_foo
#    for i in range(ITERS):
#        x = g_foo

def test_inst_member():
    class C(object):
        def __init__(self):
            self.x = 100
        @timed
        def tst_inst_member(self):
            for i in range(ITERS):
                y = self.x
    c = C()
    c.tst_inst_member()

def test_class_member():
    class C(object):
        x = 100
        @timed
        def tst_class_member(self):
            for i in range(ITERS):
                y = self.x
    c = C()
    c.tst_class_member()

#import dis
#dis.dis(test_global)
#print "-" * 80
#dis.dis(test_local)

test_global()
test_local()
#test_g()
#test_g_rebound()
test_othermod()
#test_othermod2()
test_inst_member()
test_class_member()



def x1():
    x = GLOBAL

def x2():
    global GLOBAL
    x = GLOBAL

#import dis
#dis.dis(x1)
#print "-" * 80
#dis.dis(x2)
