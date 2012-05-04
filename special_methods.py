"""
I abandoned this because I was trying to leverage base type implementation but this doesn't seem to work for 
some builtin types, e.g.

>>> import types

>>> types.IntType
<type 'int'>

>>> types.IntType.__lt__
<method-wrapper '__lt__' of type object at 0x000000001E28FC50>


>>> types.IntType.__lt__(3,5)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: expected 1 arguments, got 2

>>> types.IntType.__lt__(3)
NotImplemented

>>> dict.__lt__
<slot wrapper '__lt__' of 'dict' objects>
# why is this slot wrapper and not method-wrapper?....wtf

>>> dict.__lt__({1:1}, {2:2})
NotImplemented

>>> dict.__lt__({1:1})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: expected 1 arguments, got 0

# too many inconsistencies in python...annoying
<built-in method bit_length of int object at 0x0000000001D76498>
>>> n.bit_length()
3
>>> 5.bit_length()
  File "<stdin>", line 1
    5.bit_length()
               ^
SyntaxError: invalid syntax

"""

import copy
import cStringIO as StringIO
from functools import wraps
import logging
logging.basicConfig()
log = logging.getLogger()

class g:
    indent = 0

def logged(func):
    @wraps(func)
    def logged_wrapper(*args, **kwargs):
        name = func.__name__
        #ignore = (name=="__getattribute__" and args[1] == "value")
        ignore = False
        if not ignore:
            io = StringIO.StringIO()
            io.write("%s(" % name)
            io.write(", ".join([repr(arg) for arg in args]))
            if kwargs:
                io.write(",")
                io.write(", ".join("%s=%s" % (name, repr(value)) for name, value in kwargs.items()))
            io.write(")")
            print "%sstart %s" % (g.indent * " ", io.getvalue())
            g.indent += 2
        try:
            retval = func(*args, **kwargs)
        except Exception, e:
            retval = None
            log.exception("error")
        if not ignore: 
            g.indent -= 2
            print "%send   %s => %s" % (g.indent * " ", io.getvalue(), repr(retval))
        return retval
        
    return logged_wrapper


class Metaclass(type):
    @logged
    def __new__(*args, **kwargs):
        return type.__new__(*args, **kwargs)

class intlike(int):
    __metaclass__ = Metaclass
    @logged
    def __new__(*args, **kwargs):
        return int.__new__(*args, **kwargs)
    
class stringlike(str):
    __metaclass__ = Metaclass    
    @logged
    def __new__(*args, **kwargs):
        return str.__new__(*args, **kwargs)


klasses = (intlike, stringlike)

    
    #@logged
    #def __init__(self, value):
    #    self.value = value
    #    return object.__init__(self)
        
    #@logged
    #def __del__(self):
    #    pass

    #def __repr__(self):
    #    return "Obj(%s)" % self.value
    
    #@logged    
    #def __str__(self):
    #    return "Obj(%s)" % self.value
    
    #@logged
    #def __add__(self, other):
    #    if type(other) == type(self):
    #        self.value += other.value
    #    else:
    #        self.value += other
        
    #@logged
    #def __coerce__(self, other):
    #    return None
        
    
#def create_func(methname, retval):
#    if callable(retval):
#        func = retval
#    else:
#        func = lambda *args, **kwargs : retval
#    func.__name__ = methname
#    return func    

def dictset(d, idx, value):
    d[idx] = value
    
def dictdel(d, idx):
    del d[idx]
    
def create_func(base, methname):
    def func(*args, **kwargs):
        #func = lambda *args, **kwargs : getattr(base, methname)(*args, **kwargs)
        impl = getattr(base, methname)
        print "**************"
        print methname
        print args
        print kwargs
        print "**************"
        return impl(*args, **kwargs)
    func.__name__ = methname    
    return logged(func)
    
for klass in klasses:
    base = klass.__bases__[0]
    
    # for these we just inherit superclass implementation
    for _methname in ("init", "lt", "le", "eq", "ne", "gt", "ge", "cmp", "hash", "nonzero", "unicode"):
        methname = "__%s__" % _methname
        setattr(klass, methname, create_func(base, methname))
        
    # these require some customization        
    for methname, factory in [
                           #("__new__",          lambda base : lambda *args, **kwargs : base.__new__(*args, **kwargs)),
                           #("__init__",         lambda base : lambda *args, **kwargs : base.__init__(*args, **kwargs)),
                           #("__lt__",           lambda base : lambda *args, **kwargs : base.__lt__(*args, **kwargs)),
                           #("__le__",           lambda self, other : self.value.__le__(type(self.value)(other))),
                           #("__eq__",           lambda self, other : self.value.__eq__(type(self.value)(other))), 
                           #("__ne__",           lambda self, other : self.value.__ne__(type(self.value)(other))),
                           #("__gt__",           lambda self, other : self.value.__gt__(type(self.value)(other))),
                           #("__ge__",           lambda self, other : self.value.__ge__(type(self.value)(other))),
                           #("__cmp__",          lambda self, other : cmp(self.value, type(self.value)(other))),
                           #("__rcmp__",          lambda self, other : cmp(self.value, type(self.value)(other))),
                           #("__hash__",         lambda self : hash(self.value)),
                           #("__nonzero__",      lambda self : self.value != 0),
                           #("__unicode__",      lambda self : u"%s" % self.value),
                           ("__getattr__",      lambda base : lambda self, attr : self.__dict__[attr]),
                           ("__setattr__",      lambda base : lambda self, attr, value : dictset(self.__dict__, attr, value)),
                           ("__delattr__",      lambda base : lambda self, attr : dictdel(self.__dict__, attr)),
                           ("__getattribute__", lambda base : lambda self, attr : object.__getattribute__(self, attr)),
                           
                           # TODO: __get__, __set__, __delete__
                           
                           #("__del__",          lambda *args : None), 
                           #("__add__",          lambda self, other : self.value.__add__(type(self.value)(other))), 
                           #("__mul__",          lambda self, other : self.value.__mul__(type(self.value)(other))),
                           
                           
                           #("__int__",          lambda self : int(self.value)),
                           
                           
                           ]:
        
        #method = new.instancemethod(lambda *args, **kwargs : getattr(object, methname)(*args, **kwargs), None, A)
        #method = new.instancemethod(lambda *args, **kwargs : 0, None, A)
        #func = create_func(methname, retval)
        func = factory(base)
        func.__name__ = methname
        setattr(klass, methname, logged(func))
        
        #for klass in (A, B, C):
        #    setattr(klass, methname, logged(func))
        #A.__dict__[methname] = method
        #def __new__(*args, **kwargs):
        #    return object.__new__(*args, **kwargs)

    
