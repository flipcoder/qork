#!/usr/bin/env python

from copy import copy
from .util import *

class Signal:
    def __init__(self, **kwargs):
        self.slots = {}
        self.meta = {}
        # self.allow_break = kwargs.get('allow_break')
        self.force_break = kwargs.get('force_break') or False
        self.include_context = kwargs.get('include_context') or False
        self.call_options = kwargs.get('call_options')
        self.accumulator_func = None
        self._block = False
    def accumulator(self, func=DUMMY):
        if func is DUMMY:
            return self.accumulator_func
        self.accumulator_func = func
        return func
    def ensure(self, func, context=''):
        if context not in self.slots:
            self.connect(func, context)
            return
        if func not in self.slots[context]:
            self.connect(func, context)
    def connect(self, func, context='', **kwargs):
        assert func
        once = kwargs.get('once')
        assert context != '' or not once # once requires context
        if context:
            self.meta[context] = {
                'hidden':  kwargs.get('hidden'),
                'once':  once,
            }
        if context not in self.slots:
            self.slots[context] = []
        self.slots[context].append(func)
    def once(self, func, context='', **kwargs):
        kwargs['once'] = True
        return self.connect(func, context, **kwargs)
    def clear(self):
        self.slots = {}
    def disconnect(self, context):
        try:
            del self.slots[context]
            return True
        except KeyError:
            return False
    def blocked(self, b):
        return self._block
    def block(self, b=True):
        self._block = b
    def __call__(self, *args, **kwargs):
        if not self.slots or self._block:
            return
        context = kwargs.get('context', None)
        if self.call_options:
            # brk = kwargs.get('allow_break', False)
            brk = False
            force_break = kwargs.get('force_break', False)
            include_context = kwargs.get('include_context', False)
        else:
            # brk = self.allow_break
            brk = False
            force_break = self.force_break
            include_context = self.include_context
        items_copy = list(self.slots.items()).copy()
        breakout = False
        accumulated = []
        triggered = False
        for ctx, funcs in items_copy:
            if not context or ctx in context:
                funcs_copy = funcs.copy()
                for func in funcs_copy:
                    r = DUMMY
                    if include_context:
                        r = func(ctx, *args)
                        triggered = True
                    else:
                        r = func(*args)
                        triggered = True
                    if self.accumulator_func:
                        accumulated.append(r)
                    if brk and r is not DUMMY:
                        breakout = True
                        break
                    if force_break:
                        breakout = True
                        break
            if breakout:
                break
        for meta,ops in self.meta.items():
            if ops['once']:
                self.disconnect(meta)
        if accumulated:
            return accumulator_func(accumulated)
        return triggered

class Reactive:
    def __init__(self, value=None, callbacks=[]):
        self.value = value
        self.on_change = Signal()
        for func in callbacks:
            self.on_change.connect(func)
    def connect(self, func):
        return self.on_change.connect(func)
    def __call__(self, value=DUMMY):
        if value is DUMMY:
            return self.value
        oldvalue = self.value
        self.value = value
        self.on_change(value, oldvalue) # new, old
    def block(self, b):
        self.on_change.block(b)
    def do(self, func):
        oldvalue = self.value
        self.value = func(self.value)
        self.on_change(self.value, oldvalue)
        return self.value

class Lazy:
    def __init__(self, func, capture=[], callbacks=[]):
        self.func = func
        self.fresh = False
        self.value = None
        self.on_pend = Signal()
        for sig in capture:
            sig.connect(self.pend)
        for func in callbacks:
            self.on_pend.connect(func)
    def __call__(self):
        self.ensure()
        return self.value
    def connect(self, func):
        return self.on_pend.connect(func)
    def set(self, v):
        if callable(v):
            self.func = v
            self.fresh = False
            self.on_pend()
        else:
            self.value = v
            self.fresh = True
            self.on_pend()
    def pend(self):
        self.on_pend()
        self.fresh = False
        self.value = None
    def ensure(self):
        if not self.fresh:
            self.recache()
    def recache(self):
        self.value = self.func()
        self.fresh = True
        self.on_pend()
    def available(self):
        return self.value is not None
    def try_get(self):
        return self.value

