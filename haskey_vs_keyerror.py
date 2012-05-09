"""
Test when key exists
-----------------------------
Obviously, the try/except is fastest in this case, and using get is 2x slower
test_has_key: 195.16796 msecs
test_get: 175.30111 msecs
test_keyerror: 84.13955 msecs

Test when key does not exist
------------------------------
test_has_key: 144.31262 msecs
test_get: 173.68451 msecs
test_keyerror: 889.99377 msecs

THIS IS COUNTERINTUITIVE! checking has_key is faster than get in this case!

Conclusion: if you are pretty sure the key will be there, use try/except KeyError, else use
  has_key

"""
import sys
import time
from decorators import timed
import ujson
import copy
import cPickle as pickle
import marshal

ITERS = range(1000000)

D = {"foo":1}
KEY = "bar"

@timed
def test_has_key():
    for i in ITERS:
        if D.has_key(KEY):
            x = D[KEY]
        else:
            x = None

@timed
def test_get():
    for i in ITERS:
        x = D.get(KEY, None)

@timed
def test_keyerror():
    for i in ITERS:
        try:
            x = D[KEY]
        except KeyError:
            x = None

test_has_key()
test_get()
test_keyerror()

