#!/usr/bin/env python

from .factory import *
from .resource import *

class CacheException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

def deref(self):
    assert self._count > 0
    self._count -= 1

class Cache(Factory):
    def __init__(self, resolver=None, transformer=None):
        super().__init__(resolver, transformer)
        self.resources = {}
        self.cleanup_list = []
    def __call__(self, *args, **kwargs):
        fn = None
        for arg in args: # check args for filename
            if isinstance(arg,str):
                fn = arg
                break
        assert fn
        if fn in self.resources:
            r = self.resources[fn]
            r._count += 1
            return r
        r = super().__call__(*args, **kwargs)
        r._cache = self
        r._count = 1
        assert not hasattr(r,'deref')
        r.deref = deref
        self.resources[fn] = r
        return r
    def has(self, fn):
        return fn in self.resources
    def ensure(self, fn, data):
        if fn in self.resources:
            return self.resources[fn]
        data.deref = lambda data=data: deref(data)
        data._cache = self
        data._count = 1
        self.resources[fn] = data
        return data
    def overwrite(self, fn, data):
        if fn in self.resources:
            res = self.resources[fn]
            if hasattr(res,'cleanup') and callable(res.cleanup):
                res.cleanup()
            del self.resources[fn]
        data.deref = lambda data=data: deref(data)
        data._cache = self
        data._count = 1
        self.resources[fn] = data
        return data
    def typed(self, Type, *args, **kwargs):
        r = self.__call__(self, *args, **kwargs)
        assert isinstance(r(), Type)
        return r
    def count(self, fn):
        if fn == None:
            return len(self.resources)
        return self.resources[fn]._count
    def clear(self):
        for fn,res in self.resources.items():
            if hasattr(res,'cleanup') and callable(res.cleanup):
                res.cleanup()
        self.resources = []
        for resource in self.cleanup_list:
            if hasattr(res,'cleanup') and callable(res.cleanup):
                res.cleanup()
        self.cleanup_list = []
    def clean(self):
        remove = []
        count = 0
        remaining = 0
        for fn,res in self.resources.items():
            if res._count == 0:
                if hasattr(res,'cleanup') and callable(res.cleanup):
                    res.cleanup()
                remove.append(fn)
                count += 1
            else:
                remaining+= 1
        if remove:
            self.resources = filter(lambda r: r not in remove, self.resources)
        for res in self.cleanup_list:
            if hasattr(res,'cleanup') and callable(res.cleanup):
                res.cleanup()
            count += 1
        self.cleanup_list = []
        return count, remaining
