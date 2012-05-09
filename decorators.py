import time
import atexit
import logging
log = logging.getLogger()

_timedfuncs = {} # func.__name__ -> (min, max, total, numcalls)

def dumpTimings(printfunc=None):
    funcs = _timedfuncs.keys()
    funcs.sort()
    for func in funcs:
        info = _timedfuncs[func]
        msg = ("%s: min=%3.5f msec, max=%3.5f msec, avg=%3.5f msec, numcalls=%d" % (func, 
                                info[0], info[1], info[2]/float(info[3]), info[3]))
        if printfunc:
            printfunc(msg)
        else:
            print msg

atexit.register(dumpTimings)

def timed(func, printfunc=None, printif=lambda elapsed : True):
    def timed_wrapper(*args, **kw):
        start = time.clock()
        try:
            return func(*args, **kw)
        finally:
            elapsed = (time.clock() - start) * 1000.0
            info = _timedfuncs.setdefault(func.__name__, [999999, 0, 0, 0])
            if elapsed < info[0]:
                info[0] = elapsed
            if elapsed > info[1]:
                info[1] = elapsed
            info[2] = info[2] + elapsed
            info[3] = info[3] + 1
            _timedfuncs[func.__name__] = info
            if printif and printif(elapsed):
                msg = "%s: %.5f msecs" % (func.__name__, elapsed)
                if printfunc:
                    printfunc(msg)
                else:
                    print msg
    try:
        timed_wrapper.__name__ = func.__name__
    except TypeError:
        pass # python 2.3 doesn't allow assigning to __name__
    timed_wrapper.__dict__ = func.__dict__
    timed_wrapper.__doc__ = func.__doc__
    # save a handle to the wrapped function so it can be accessed if needed
    timed_wrapper._wrapped_function = getattr(func, "_wrapped_function", None) or func
    return timed_wrapper

