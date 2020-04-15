#!/usr/bin/env python

from copy import copy
from .util import *
from .signal import *
import glm
import enum


class WeakLambda:
    """
    WeakLambda([a, b], lambda a, b: a + b)
    a and b are stored as weakrefs and dereferenced on call

    Fails silently if any parameter fails dereference.
    """

    # Error = enum.Enum('WeakLambda.Error', 'Dereference')

    def __init__(self, capture, func):  # , errors=False):
        self.func = func
        self.dead = False
        # self.errors = errors
        self.capture = tuple(weakref.ref(var) for var in capture)

    def __call__(self, *args):
        if self.func is None:
            self.dead = True
            return None
        capture = tuple(x() for x in self.capture)
        if None not in capture:
            return self.func(*capture, *args)
        # if self.errors:
        #     raise ErrorCode(Error.Dereference)
        self.dead = True
        return None

    # def clear():
    #     self.dead = True
    #     self.capture = []
    #     self.func = None


class Reactive:
    """
    Variable with an on_change() signal
    """

    def __init__(self, value=None, callbacks=[], retrigger=False, transform=None):
        self.value = value
        self.transform = transform
        self.on_change = Signal()
        self.on_pend = Signal()  # same as on_change but no change value
        self.retrigger = retrigger

        if callbacks:
            self.on_change += callbacks

    def set(self, value):
        if not self.transform:
            self.value = value
        else:
            self.value = self.transform(value)

    def pend(self):
        self.on_pend()
        self.on_change(self.value)

    def connect(self, func, weak=True, on_remove=None):
        return self.on_pend.connect(func, weak=weak, on_remove=on_remove)

    def __iadd__(self, func):
        self.on_change += func
        return self

    def __isub__(self, func):
        self.on_pend -= func
        self.on_change -= func
        return self

    def __bool__(self):
        return bool(self.value)

    def __call__(self, value=DUMMY):
        if value is DUMMY:
            return self.value
        if not self.retrigger:
            oldvalue = self.value
        self.value = value
        # self.on_change(value, oldvalue)  # new, old
        if not self.retrigger or oldvalue != self.value:
            self.on_change(value)

    def do(self, func):
        if not self.retrigger:
            oldvalue = self.value
        self.value = func(self.value)
        if not self.retrigger or oldvalue != self.value:
            self.on_change(self.value)
        return self.value

    # for reactive lists + dictionaries:

    def __getitem__(self, idx):
        return self.value[idx]

    def __setitem__(self, idx, value):
        self.value[idx] = value
        self.on_change(self.value)

    def append(self, idx, value):
        self.value.add(value)
        self.on_change(self.value)

    def pop(self, *args):
        self.value.pop(*args)
        self.on_change(self.value)

    def push(self, *args):
        self.value.push(*args)
        self.on_change(self.value)

    def append(self, *args):
        self.value.append(*args)
        self.on_change(self.value)


class Rvec(Reactive):
    """
    Reactive Vector 3
    """

    def __init__(self, value=None, callbacks=[], Type=glm.vec3):
        super().__init__(value, callbacks)
        self.Type = Type
        self.value = Type()

    def set(self, v):
        self.value.set(v)

    @property
    def xy(self):
        return self.value.xy

    @property
    def xyz(self):
        return self.value.xyz

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

    @property
    def w(self):
        return self.value.w

    @w.setter
    def w(self, newz):
        self.value.w = s
        if old.w != neww:
            self.on_change(self.value, old)


class Lazy:
    def __init__(self, func, capture=[], callbacks=[]):
        self.func = func
        self.fresh = False
        self.value = None
        self.on_pend = Signal()
        self.connections = Connections()
        cls = self.__class__
        for sig in capture:
            self.connections += sig.connect(
                self.pend,
                on_remove=lambda s, ws=weakref.ref(self): cls.weak_remove(ws, s),
            )
        for func in callbacks:
            try:
                func.connections
            except AttributeError:
                self.on_pend.connect(func, weak=False)
                continue
            func.connections += self.on_pend(func)

    @weakmethod
    def weak_remove(self, slot):
        self.connections.remove(slot)

    def __call__(self):
        self.ensure()
        return self.value

    def connect(self, func, weak=True, on_remove=None):
        return self.on_pend.connect(func, weak, on_remove=on_remove)

    def set(self, v):
        if callable(v):
            self.func = v
            self.fresh = False
            self.on_pend()
        else:
            self.value = v
            self.fresh = True
            self.on_pend()

    def pend(self, *args, **kwargs):  # args just in case signal calls this
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


def lazy(cls):
    """
    Lazy function decorator
    Captures reactive dependencies and generates Lazy(func)
    """


def reactive(cls):
    """
    Class Decorator
    Generate props/setters for all the reactive "_members" of the class
    """

    def wrapper():

        return cls

    return wrapper
