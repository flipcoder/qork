#!/usr/bin/env python

from copy import copy

# from .util import *
from .signal import *
import glm
import enum
import traceback


class Dummy:
    pass


DUMMY = Dummy()

try:
    weakmethod
except:

    def weakmethod(func):
        """
        Weak Method decorator
        class A:
            @weakmethod
            def test(weakself, *args):
                pass
        """

        def f(weakself, *args, **kwargs):
            self = weakself()
            if self:
                return getattr(self, func.__name__)(*args, **kwargs)
            # elif throws:
            #     raise throws

        return f


"""
Reactive and Lazy objects and decorators using signals:

x = Reactive(lambda val: print('x is', val))
x(5) # 'x is 5'
x += lambda: print('you changed x!')
x(6) # 'x is 5', 'You changed x!'

Using Properties:

    class Foobar:
        def __init__(self):
            self._x = Reactive(0, lambda x: print('you changed x!'))

    foobar = Foobar()
    foobar.x += lambda: print('you changed x!')
    foobar.x = 5 # you changed x!

class Foobar:
    @lazy(multiple)
    def x(self):
        return math.pi * multiple
"""


class WeakLambda:
    """
    WeakLambda([a, b], lambda a, b: a + b)
    a and b are stored as weakrefs and dereferenced on call

    Fails silently if any parameter fails dereference.
    """

    # Error = enum.Enum('WeakLambda.Error', 'Dereference')

    def __init__(self, capture, func, errors=True):
        self.func = func
        self._dead = False

        self.capture = tuple(weakref.ref(var) for var in capture)

    def __call__(self, *args):
        if self.func is None:
            self.dead = True
            return None
        capture = tuple(x() for x in self.capture)
        if None not in capture:
            return self.func(*capture, *args)
        self._dead = True
        return None

    def dead(self):
        if self._dead:
            return True
        if self.func is None:
            self._dead = True
            return True
        capture = tuple(x() for x in self.capture)
        if None in capture:
            self._dead = True
            return True

    # def clear():
    #     self.dead = True
    #     self.capture = []
    #     self.func = None


class TrackMe:
    def __init__(self, value):
        self.value = value

    # def __get__(self, obj, objtype):
    #     return self.value if objtype else self
    # def __set__(self, obj, val):
    #     traceback.print_stack()
    #     print('set:', val)
    #     self.value = val
    def __call__(self, val=DUMMY):
        if val is DUMMY:
            return self.value
        else:
            print("trackme call")
            traceback.print_stack()
            self.value = val


class Reactive:
    """
    Variable with an on_change() signal
    """

    def __init__(
        self,
        value=None,
        callbacks=[],
        observe=[],
        prop=True,
        retrigger=False,
        transform=None,
    ):
        observe = list(observe or [])
        callbacks = list(callbacks or [])

        self.value = value
        self.transform = transform
        self.on_change = Signal()
        self.on_pend = Signal()  # same as on_change but no change value
        self.retrigger = retrigger
        self.connections = Container()

        if not observe:
            try:
                if self.func._observe is not None:
                    observe += self.func._observe
            except AttributeError:
                pass
        cls = self.__class__
        for sig in observe:
            self.connections += sig.connect(
                lambda *a, **kwa: self.pend(),
                on_remove=lambda s, ws=weakref.ref(self): cls.weak_remove(ws, s),
            )

        if callbacks:
            for cb in callbacks:
                try:
                    self.on_pend += cb.pend
                except AttributeError:
                    self.on_pend += cb

        # self.is_func = callable(self.value)
        # self.cached = None

        # if self.is_func:
        #     self.value = self.value()
        #     self.pend()

    @weakmethod
    def weak_remove(self, slot):
        self.connections -= slot

    # def __lshift__(self, b):
    #     self.set(b)
    #     return self

    # def __ilshift__(self, b):
    #     self.set(b)
    #     return self

    def set(self, value):
        # self.is_func = callable(v)
        self.value = self.transform(value) if self.transform else value
        # if self.is_func:
        # self.cached = self.value()

    def pend(self):
        self.on_change(self.value)
        self.on_pend()

    def connect(self, func, weak=True, on_remove=None):
        return self.on_pend.connect(func, weak=weak, on_remove=on_remove)

    def __iadd__(self, func):
        if callable(func):
            self.on_change += func
        else:
            self(self.value + func)  # func is just a value, do +=
        return self

    def __isub__(self, func):
        if callable(func):
            self.on_pend -= func
            self.on_change -= func
        else:
            self(self.value - func)
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
            self.pend()

    def do(self, func):
        if not self.retrigger:
            oldvalue = self.value
        self.value = func(self.value)
        if not self.retrigger or oldvalue != self.value:
            self.pend()
        return self.value

    # for reactive lists + dictionaries:

    def __getitem__(self, idx):
        return self.value[idx]

    def __setitem__(self, idx, value):
        self.value[idx] = value
        self.pend()

    def append(self, idx, value):
        self.value.add(value)
        self.pend()

    def pop(self, *args):
        self.value.pop(*args)
        self.pend()

    def push(self, *args):
        self.value.push(*args)
        self.pend()

    def append(self, *args):
        self.value.append(*args)
        self.pend()


class ReactiveProperty(Reactive):
    def __get__(self, inst, owner):
        # print("get")
        return self() if inst else self

    def __set__(self, inst, val):
        # print("set")
        return self(val)


class ReactiveVector(Reactive):
    """
    Reactive Vector 3
    """

    def __init__(self, value=None, callbacks=[], observe=[], Type=glm.vec3):
        super().__init__(value, callbacks, observe)
        self.Type = Type
        self.value = Type()
        # TODO: generate swizzle props?

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
        old = self.value
        self.value.z = s
        if old.z != newz:
            self.on_change(self.value, old)

    @property
    def w(self):
        return self.value.w

    @w.setter
    def w(self, neww):
        old = self.value
        self.value.w = s
        if old.w != neww:
            self.pend(self.value, old)


Rvec = ReactiveVector


class ReactiveColor(Rvec):
    """
    Reactive Color
    """

    def __init__(self, value=None, callbacks=[], Type=glm.vec4):
        super().__init__(value, callbacks)
        self.Type = Type
        self.value = Type()
        # generate swizzle props?

    @property
    def r(self):
        return self.value.r

    @r.setter
    def r(self, newr):
        old = self.value
        self.value.r = newr
        if old.r != newr:
            self.on_change(self.value, old)

    @property
    def g(self):
        return self.value.g

    @g.setter
    def g(self, newg):
        old = self.value
        self.value.g = newg
        if old.g != newg:
            self.on_change(self.value, old)

    @property
    def b(self):
        return self.value.b

    @b.setter
    def b(self, newb):
        old = self.value
        self.value.b = s
        if old.b != newb:
            self.on_change(self.value, old)

    @property
    def a(self):
        return self.value.a

    @a.setter
    def a(self, newa):
        old = self.value
        self.value.a = s
        if old.a != newa:
            self.pend(self.value, old)


Rcolor = ReactiveColor


class Lazy:
    def __init__(self, func, observe=[], callbacks=[]):
        observe = list(observe or [])  # python mutable default param bug
        callbacks = list(callbacks or [])  # "

        self.func = func
        self.fresh = False
        self.value = None
        self.on_pend = Signal()
        self.connections = Connections()
        if not observe:
            try:
                if func.observe is not None:
                    observe += func.observe
            except AttributeError:
                pass
        cls = self.__class__
        for sig in observe:
            ws = weakref.ref(self)
            self.connections += sig.connect(
                self.pend,
                on_remove=lambda s, ws=ws: cls.weak_remove(ws, s),
            )
        for func in callbacks:
            try:
                func = func.pend
            except AttributeError:
                pass

            try:
                func.connections
            except AttributeError:
                self += func
                continue
            func.connections += self.connect(func)

    @weakmethod
    def weak_remove(self, slot):
        self.connections -= slot

    def __call__(self, v=DUMMY, lazy=None):
        # get
        if v is DUMMY:
            self.ensure()
            return self.value

        # set
        # if callable(v):
        #     self.func = v
        #     self.fresh = False
        # else:
        if lazy is not None:
            self.func = lazy
            self.fresh = False
        else:
            self.value = v
            self.fresh = True
            self.on_pend()

    # def reset(self, func):
    #     # set
    #     pass

    def __iadd__(self, func):
        self.on_pend.connect(func, weak=False)
        return self

    def __isub__(self, func):
        self.on_pend.disconnect(func)
        return self

    def connect(self, func, weak=True, on_remove=None):
        return self.on_pend.connect(func, weak, on_remove=on_remove)

    def pend(self, *args, **kwargs):  # args just in case signal calls this
        self.fresh = False  # mark dirty
        self.value = None
        self.on_pend()

    def ensure(self):
        if not self.fresh:
            self.recache()

    def recache(self):
        self.value = self.func()
        self.fresh = True
        self.on_pend()

    def available(self):
        return self.value is not None

    # def get(self):
    #     return self.value


def observe(*deps):
    def observe_decorator(func):
        func.observe = deps
        return func

    return observe_decorator


def callbacks(*callbacks):
    def callback_decorator(func):
        func.callbacks = callbacks
        return func

    return observe_decorator


def lazy(*deps, **kwargs):
    def lazy_decorator(func):
        return Lazy(
            func,
            observe=deps or kwargs.get("observe", []),
            callbacks=deps or kwargs.get("callbacks", []),
        )

    return lazy_decorator


def reactive(*args, **kwargs):
    """
    INCOMPLETE

    Class or Function Decorator
    For classes: Generate props/setters for all the reactive "_members" of the class
    The class must "templatable", meaning a default arg version must contain
    the reactive members you wish to expose to the overall class
    """
    if args and type(args[0]) == type:
        # class decorator
        # INCOMPLETE
        cls = args[0]

        def reactive_class_decorator(cls):
            template = cls()  # TODO: check for dataclass members?
            for name, r in template.__dict__.items():
                if not name.startswith("__") and name[0] == "_":
                    if not isinstance(r, Reactive):
                        continue
                    prop = property(r)
                    setattr(cls, name[1:], prop)
                    prop.setter(r)

        return reactive_class_decorator

    # function decorator

    # observe arguments unless a function is given (this means no decorator params)
    obs = args if args and not callable(args[0]) else []

    def reactive_decorator(func):
        return Reactive(
            func,
            observe=obs or kwargs.get("observe", []),
            callbacks=kwargs.get("callbacks", []),
        )

    if args and callable(args[0]):  # function (no decorator params)
        assert len(args) == 1
        return lazy_decorator(func)

    return lazy_decorator
