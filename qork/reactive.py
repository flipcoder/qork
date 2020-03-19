#!/usr/bin/env python

from .util import *

class Signal:
    def __init__(self, **kwargs):
        self.slots = {}
        self.meta = {}
        # self.allow_break = kwargs.get('allow_break')
        self.force_break = kwargs.get('force_break') or False
        self.include_context = kwargs.get('include_context') or False
        self.limit_context = kwargs.get('limit_context')
        self.call_options = kwargs.get('call_options')
    def ensure(self, func, context=''):
        if context not in self.slots:
            self.connect(func, context)
            return
        if func not in self.slots[context]:
            self.connect(func, context)
    def connect(self, func, context='', **kwargs):
        if context:
            self.meta[context] = {
                'hidden':  kwargs.get('hidden')
            }
        if context not in self.slots:
            self.slots[context] = []
        self.slots[context].append(func)
    def clear(self):
        self.slots = {}
    def disconnect(self, context):
        try:
            del self.slots[context]
            return True
        except KeyError:
            return False
    def __call__(self, *args, **kwargs):
        if not self.slots:
            return
        if self.call_options:
            limit_context = kwargs.get('limit_context', None)
            # brk = kwargs.get('allow_break', False)
            force_break = kwargs.get('force_break', False)
            include_context = kwargs.get('include_context', False)
        else:
            limit_context = self.limit_context
            # allow_break = self.allow_break
            force_break = self.force_break
            include_context = self.include_context
        items_copy = copy(self.slots.items())
        for ctx, funcs in items_copy:
            if not limit_context or ctx in limit_context:
                funcs_copy = copy(funcs)
                for func in funcs_copy:
                    r = None
                    if include_context:
                        r = func(ctx, *args)
                    else:
                        r = func(*args)
                    if brk and r:
                        return
                    if force_break:
                        return

class Lazy:
    def __init__(self, func):
        self.func = func
        self.fresh = False
        self.value = None
    def __call__(self):
        self.ensure()
        return self.value
    def set(self, v):
        if callable(v):
            self.func = v
            self.fresh = False
        else:
            self.value = v
            self.fresh = True
    def pend(self):
        self.fresh = False
        self.value = None
    def ensure(self):
        if not self.fresh:
            self.recache()
    def recache(self):
        if is_lambda(self.func):
            self.value = self.func(None)
        else:
            self.value = self.func()
        self.fresh = True

