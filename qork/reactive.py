#!/usr/bin/env python

import types

class Signal:
    def __init__(self):
        self.slots = {}
        self.meta = {}
    def ensure(self, func, context=''):
        if context not in self.slots:
            self.connect(func, context)
            return
        if func not in self.slots[context]:
            self.connect(func, context)
    def connect(self, func, context='', hidden=False):
        if context:
            self.meta[context] = {
                'hidden':  hidden
            }
        if context not in self.slots:
            self.slots[context] = []
        self.slots[context] += [func]
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
        limit_context = kwargs.get('limit_context', None)
        brk = kwargs.get('allow_break', False)
        force_brk = kwargs.get('force_break', False)
        include_context = kwargs.get('include_context', False)
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
                    if force_brk:
                        return

class Lazy:
    def __init__(self, func):
        self.func = func
        self.fresh = False
        self.value = None
        self.is_lambda = isinstance(self.func, types.LambdaType) and \
            self.func.__name__ == '<lambda>'
    def __call__(self):
        self.ensure()
        return self.value
    def pend(self):
        self.fresh = False
        self.value = None
    def ensure(self):
        if not self.fresh:
            self.recache()
    def recache(self):
        if self.is_lambda:
            self.value = self.func(None)
        else:
            self.value = self.func()
        self.fresh = True

