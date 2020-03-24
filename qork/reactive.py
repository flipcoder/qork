#!/usr/bin/env python

from copy import copy
from .util import *
from .signal import *


class Reactive:
    def __init__(self, value=None, callbacks=[]):
        self.value = value
        self.on_change = Signal()
        for func in callbacks:
            self.on_change.connect(func, weak=False)

    def connect(self, func, weak=True):
        return self.on_change.connect(func, weak)

    def __call__(self, value=DUMMY):
        if value is DUMMY:
            return self.value
        oldvalue = self.value
        self.value = value
        self.on_change(value, oldvalue)  # new, old

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
            sig.connect(self.pend, weak=False)
        for func in callbacks:
            self.on_pend.connect(func, weak=False)

    def __call__(self):
        self.ensure()
        return self.value

    def connect(self, func, weak=True):
        return self.on_pend.connect(func, weak)

    def set(self, v):
        if callable(v):
            self.func = v
            self.fresh = False
            self.on_pend()
        else:
            self.value = v
            self.fresh = True
            self.on_pend()

    def pend(self, *args):  # *args just in case signal calls this
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
