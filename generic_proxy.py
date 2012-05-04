# Kevin T. Manley (kevin.manley@gmail.com)
# This improves on a pattern described in the Python Cookbook (6.6 Delegating Special Methods in Proxies)
# and adds ideas from http://code.activestate.com/recipes/519639-true-lieberman-style-delegation-in-python/

import new
from types import MethodType

class Proxy(object):
    def __init__(self, obj):
        if type(obj) != self._required_type:
            raise TypeError("%s expected a %s argument, got %s instead" % (self.__class__.__name__, 
                                                                           self._required_type, type(obj)))
        super(Proxy, self).__init__()
        self._obj = obj
        self._attr_cache = {}
        
    def __getattr__(self, name):
        print "DEBUG: __getattr__(%s)" % name
        attr_cache = self._attr_cache
        try:
            return attr_cache[name]
        except KeyError:
            obj = self._obj
            val = getattr(obj, name)
            if isinstance(val, MethodType):
                val = new.instancemethod(val.im_func, self, obj.__class__)
            attr_cache[name] = val
            return val

def make_binder(unbound_method):
    def f(self, *args, **kwargs):
        print "DEBUG: %s(%s, %s) called" % (unbound_method, args, kwargs) 
        return unbound_method(self._obj, *args, **kwargs)
    return f
    
_PROXY_CLASS_CACHE = {}
_FORWARDED_METHODS = set(["__%s__" % x for x in ("add", "cmp", "contains", "delattr", "delitem", "delslice", "eq", "format",
                                                 "ge", "getitem", "getslice", "gt", "hash", "iadd", "imul", 
                                                 "iter", "le", "len", "lt", "mul", "ne", "repr", "reversed", "rmul", "setitem",
                                                 "setslice", "str")])

def proxy_class_factory(obj_cls):
    """Factory function for Proxies that can delegate special methods."""
    proxy_cls = _PROXY_CLASS_CACHE.get(obj_cls)
    if not proxy_cls:
        #Synthesize proxy class on the fly
        proxy_cls = type("%sProxy" % obj_cls.__name__.title(), (Proxy,), {"_required_type" : obj_cls})

        #Add special double-underscore methods
        for name in dir(obj_cls):
            if (name in _FORWARDED_METHODS):
                unbound_method = getattr(obj_cls, name)
                setattr(proxy_cls, name, make_binder(unbound_method))
        
        _PROXY_CLASS_CACHE[obj_cls] = proxy_cls
        
    return proxy_cls


