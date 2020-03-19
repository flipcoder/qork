#!/usr/bin/env python

from .factory import *
from .resource import *

class Cache(Factory):
    def __init__(self):
        super().__init__()
        self.resources = {}
    def __call__(self, *args, **kwargs):
        fn = None
        for arg in args: # check args for filename
            if isinstance(arg,str):
                fn = arg
                break
        assert fn
        if fn in self.resources:
            r = self.resources[fn]
            r.count += 1
            return r
        r = super().__call__(*args, **kwargs)
        r.resource_cache = r
        r.resource_count = 1
        self.resources[fn] = r
        return r
    def cache_direct(self, fn, data):
        if fn in self.resources:
            return self.resources[fn]
        self.resources[fn] = data
        return data
    def cache_overwrite(self, fn, data):
        if fn in self.resources:
            res = self.resources[fn]
            res.cleanup()
            del self.resources[fn]
        self.resources[fn] = data
        return data
    def cache_as(self, Type, *args, **kwargs):
        r = self.__call__(self, *args, **kwargs)
        assert isinstance(r(), Type)
        return r
    def count(self, fn):
        if fn == None:
            return len(self.resources)
        return self.resources[fn].count
    def clean(self):
        for fn,resource in self.resources.items():
            if resource.count == 0:
                resource.cleanup()
                remove.append(fn)
        if remove:
            self.resources = filter(lambda r: r not in remove, self.resources)

