# The python docs for heapq, in the example priority queue, shows using itertools.counter. I was curious why...is it faster?
# Conclusion: no it's not faster...the straightforward c+=1 is faster

from bw.util.decorators import timed
import itertools

MAX = 10000000

c = itertools.count()

@timed
def test_itertools():
  n = 0
  while n < MAX:
    n = c.next()

@timed
def test_ctr():
  c = 0
  while c < MAX:
    c += 1


test_itertools()
test_ctr()
