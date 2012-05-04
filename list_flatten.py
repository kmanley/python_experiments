"""

"""
import itertools
import operator
import timeit


mapping = {"s%d" % x : x for x in range(10)}

def test_old():
    items = []
    for pair in mapping.iteritems():
        items.extend(pair)

def test_new1():
    items = [x for pair in mapping.iteritems() for x in pair]

def test_new1b():
    items = [x for pair in mapping.items() for x in pair]

def test_new1c():
    items = [x for pair in mapping.items() for x in pair]

def test_new2():
    items = list(itertools.chain.from_iterable(mapping.iteritems()))
    
def test_new3():
    items = reduce(operator.iadd, mapping.items(), [])    

ITERS = 1000
print timeit.timeit("test_old()", "from __main__ import test_old", number=ITERS)
print timeit.timeit("test_new1()", "from __main__ import test_new1", number=ITERS)
print timeit.timeit("test_new1b()", "from __main__ import test_new1b", number=ITERS)
print timeit.timeit("test_new1c()", "from __main__ import test_new1c", number=ITERS)
print timeit.timeit("test_new2()", "from __main__ import test_new2", number=ITERS)
print timeit.timeit("test_new3()", "from __main__ import test_new3", number=ITERS)
#test_len()
#test_indexerror()

