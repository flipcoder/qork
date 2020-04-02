#!/usr/bin/env python

from copy import copy
from .util import *
from .signal import *
import glm


class Reactive:
    def __init__(self, value=None, callbacks=[]):
        self.value = value
        self.on_change = Signal()
        self.on_change += callbacks

    def connect(self, func, weak=True):
        return self.on_change.connect(func, weak)

    def __iadd__(self, func):
        self.on_change += func

    def __isub__(self, func):
        self.on_change -= func

    def __bool__(self):
        return bool(self.value)

    def __call__(self, value=DUMMY):
        if value is DUMMY:
            return self.value
        oldvalue = self.value
        self.value = value
        # self.on_change(value, oldvalue)  # new, old
        self.on_change(value)

    def do(self, func):
        # oldvalue = self.value
        self.value = func(self.value)
        # self.on_change(self.value, oldvalue)
        self.on_change(self.value)
        return self.value

    # for reactive lists + dictionaries:

    def __getitem__(self, idx):
        return self.value[idx]

    def __setitem__(self, idx, value):
        self.value[idx] = value

    def append(self, idx, value):
        self.value.add(value)

    def pop(self, *args):
        self.value.pop(*args)

    def push(self, *args):
        self.value.push(*args)
        self.on_change()

    def append(self, *args):
        self.value.append(*args)


class Rvec3(Reactive):
    """
    Reactive Vector 3
    """

    def __init__(self, value=None, callbacks=[]):
        super().__init__(value, callbacks)
        self.value = glm.vec3()

    @property
    def x(self):
        return self.value.x

    @x.setter
    def x(self, newx):
        old = self.value
        self.value.x = newx
        if old.x != newx:
            self.on_change(self.value, old)

    @property
    def y(self):
        return self.value.y

    @y.setter
    def y(self, newy):
        old = self.value
        self.value.y = newy
        if old.y != newy:
            self.on_change(self.value, old)

    @property
    def z(self):
        return self.value.z

    @z.setter
    def z(self, newz):
        self.value.z = s
        if old.z != newz:
            self.on_change(self.value, old)


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

    def get(self):
        return self.value


def reactive(cls):
    """
    Class Decorator
    Make properties for all the reactive "_members" of the class
    """

    def wrapper():

        return cls

    return wrapper
