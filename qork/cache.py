#!/usr/bin/env python

from .factory import *
from .resource import *
import gc
import sys

from collections import defaultdict

from qork.reactive import *


# def deref(self):
#     assert self._count > 0
#     self._count -= 1


class Cache(Factory):
    WARNINGS = False
    
    def __init__(self, resolver=None, transformer=None):
        super().__init__(resolver, transformer)
        self.resources = {}
        # self.cleanup_list = []
        self.on_reload = Container(Storage=lambda: defaultdict(Signal))

    def __len__(self):
        return len(self.resources)

    def __call__(self, *args, **kwargs):
        fn = None
        func = None
        for arg in args:  # check args for filename
            if isinstance(arg, str):
                fn = arg
                break
        for arg in args:  # check args for filename
            if callable(arg):
                func = arg
                break
        assert fn
        if fn in self.resources:
            r = self.resources[fn]
            r.ref()
            # r._count += 1
            return r
        if not func:
            func = kwargs.get("load", None)
        if func:
            r = func()
        else:
            r = super().__call__(*args, **kwargs)
        r._cache = self
        r.ref(2)
        # r._count = 1
        # assert not hasattr(r, "deref")
        # r.deref = deref
        self.resources[fn] = r
        return r

    def get(self, key, default=DUMMY):
        if default is DUMMY:
            return self.resources[key]
        else:
            return self.resources.get(key, default)

    def __getitem__(self, key, default=None):
        return self.resources[default]

    def __setitem__(self, key, value):
        self.resources[key] = value

    def has(self, fn):
        return fn in self.resources

    def ensure(self, fn, data, ref=True):
        res = self.resources.get(fn, None)
        if res is not None:
            return res
        # data.deref = lambda data=data: deref(data)
        if callable(data):
            data = data()

        data._cache = self
        if ref:
            data.ref(2) # one for us, one for caller
        # data._count = 1
        if fn:  # empty filenames are temp, don't cache
            self.resources[fn] = data
        return data

    def overwrite(self, fn, data, ref=True):
        if fn in self.resources:
            res = self.resources[fn]
            # if hasattr(res, "cleanup") and callable(res.cleanup):
            #     res.cleanup()
            del self.resources[fn]
        # data.deref = lambda data=data: deref(data)
        data._cache = self
        if ref:
            data.ref(2) # one for us, one for caller
        # data._count = 1
        if fn:
            self.resources[fn] = data
        return data

    def typed(self, Type, *args, **kwargs):
        r = self.__call__(self, *args, **kwargs)
        assert isinstance(r(), Type)
        return r

    def count(self, fn=None):
        if fn is None:
            return len(self.resources)
        if fn == "":
            return 0  # temp resources (empty name) bypass cache
        # fn is resource
        if isinstance(fn, Resource):
            return max(0, fn.refs - 1)
            # return sys.getrefcount(fn) - 2
        # fn is filename
        try:
            return max(0, self.resources[fn].refs - 1)
        except KeyError:
            return 0

    # def clear(self):
    #     count = 0
    #     for fn,res in self.resources.items():
    #         if hasattr(res,'cleanup') and callable(res.cleanup):
    #             res.cleanup()
    #             count += 1
    #     self.resources = []
    #     for resource in self.cleanup_list:
    #         if hasattr(res,'cleanup') and callable(res.cleanup):
    #             res.cleanup()
    #             count += 1
    #     self.cleanup_list = []
    #     return count
    def clean(self):
        remove = []
        remaining = 0
        for fn, res in self.resources.items():
            c = res.refs
            assert c >= 0
            if c == 1: # we're the only ref
                res.deref()
                res.cleanup()
                remove.append(fn)
            else:
                remaining += 1
        for fn in remove:
            del self.resources[fn]
        return len(remove), remaining

    def __contains__(self, obj):
        return obj in self.resources

    def flush(self):
        for fn, res in copy(self.resources).items():
            res.deref()
            if Cache.WARNINGS:
                assert res.refs == 0
            res.cleanup()
        self.resources = {}

    def finish(self):
        """
        Sanity-check function to make sure all resources were cleared
        """
        total = 0
        
        while True:
            count, remaining = self.clean()
            total += count
            if remaining == 0:
                break
            if count == 0:
                break

        return total

