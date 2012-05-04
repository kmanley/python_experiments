import time

ITERS = range(1000)

def test1():
    func = time.time
    accum = 0
    for i in ITERS:
       start = func()
       end = func()
       accum += (end - start)
    print "resolution of time.time() is %.10f" % (float(accum) / len(ITERS))

def test2():
    func = time.clock
    accum = 0
    for i in ITERS:
       start = func()
       end = func()
       accum += (end - start)
    print "resolution of time.clock() is %.10f" % (float(accum) / len(ITERS))


test1()
test2()
