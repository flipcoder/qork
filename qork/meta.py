#!/usr/bin/env python

import weakref
from .reactive import *

class Meta:
    def __init__(self, obj=None, parent=None)
        obj = self.obj = {}
        if type(parent) is weakref.ref:
            self.parent = parent
        else:
            self.parent = weakref.ref(parent) if parent else None
        for k, v in self._iterobj(obj):
            tv = type(v)
            if tv is Reactive:
                obj[k] = tv
            elif tv is dict:
                obj[k] = Meta(v)
            elif tv is dict:
                obj[k] = Meta(v)
    def __setattr__(self, k, v):
        self.obj[k]
    def __getattr__(self, v):
        return self.obj[v]

    @staticmethod
    def _iterobj(self, obj):
        try:
            obj.items
        except AttributeError:
            return enumerate(obj)
        return obj.items()
