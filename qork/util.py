#!/usr/bin/env python

import itertools
import types
import glm
import math
import enum
import glm
from glm import sign
from functools import reduce
import operator
import random
from .defs import *

class Dummy:
    pass
DUMMY = Dummy()

# WIP
def mixin(mix, attr=None):
    def mixin_decorator(cls):
        for method in mix.__dict__:
            if method.startswith("__"):
                continue

            def injected_func(self, *args, **kwargs):
                func = getattr(getattr(self, attr), method)
                return func(*args, **kwargs)

            if method not in cls.__dict__:
                print(cls, method, injected_func)
                setattr(cls, method, injected_func)
        return cls

    return mixin_decorator

class ErrorCode(Exception):
    def __init__(self, code, enum, codes=None):
        super().__init__()
        self.code = code
        self.enum = enum
        self.codes = None

    def __str__(self):
        if self.codes:
            return self.enum.__name__ + ": " + self.code.value
        else:
            return self.enum.__name__ + ": " + self.code.name


class Wrapper:
    def __init__(self, value=None):
        self.value = value

    def __call__(self, value=DUMMY):
        if value is DUMMY:
            return self.value
        self.value = value
        return value

    def do(self, func):
        self.value = func(self.value)
        return self.value


class MockApp:
    def __init__(self):
        self.cache = None
        self.ctx = None


def map_range(val, r1, r2):
    return (val - r1[0]) / (r1[1] - r1[0]) * (r2[1] - r2[0]) + r2[0]


# def mixin(cls):
#     def update(self, mixin):
#         pass

#     cls.__or__ = update
#     cls.__ior__ = update
#     cls.__ror__ = update
#     return cls


def is_lambda(func):
    return isinstance(func, types.LambdaType) and func.__name__ == "<lambda>"


def flatten(r):
    return tuple(itertools.chain(*r))


def filename_from_args(args, kwargs=None):
    fn = None
    if not args:
        return None
    for arg in args:  # check args for filename (first string)
        if isinstance(arg, str):
            fn = arg
            break
    if not fn and kwargs:  # if no filename, look it up in kwargs
        fn = kwargs.get("fn") or kwargs.get("filename") or ""
    return fn


def fcmp(a, b):
    """
    Float compare and component-wise float vector compare
    """
    if type(a) in (float, int):
        return abs(a - b) < EPSILON
    else:
        for c in range(min(len(a), len(b))):
            if abs(a[c] - b[c]) >= EPSILON:
                return False
        return True


def treedepth(tree):
    if isinstance(tree, dict):
        return max(map(treedepth, tree.values()) if tree else 0) + 1
    return 0


def treepath(tree, pth):
    return reduce(operator.getitem, pth, tree)


def recursive_each(types, e, func, path=[]):
    if isinstance(e, types):
        func(e, path)
    elif isinstance(e, dict):
        for key, child in e.items():
            recursive_each(types, child, func, path + [key])
    elif isinstance(e, list):
        for i in range(len(e)):
            recursive_each(types, e[i], func, path + [i])


def to_vec3(*args):
    if args is None:
        return None
    if type(args[0]) in (tuple, list):
        return to_vec3(*args[0])
    if args[0] is None:
        return
    lenargs = len(args)
    ta = type(args)
    if ta in (float, int):
        return glm.vec3(args)
    if ta == glm.vec3:
        return args
    elif ta == glm.vec2:
        return glm.vec3(args, 0.0)
    elif ta == glm.vec4:
        return args.xyz
    else:
        if lenargs == 3:
            return glm.vec3(*args)
        elif lenargs == 2:
            return glm.vec3(*args, 0)
        elif lenargs == 1:
            return glm.vec3(args[0])
        elif lenargs == 4:
            return glm.vec3(*args[:3])

    print(args)
    assert False


# def component_scalar(s, i):
#     if type(s) in (float,int):
#         return s
#     return s[i]


def randp3xz(scale=1):
    if type(scale) in (float, int):
        scale = vec3(scale)
    return glm.vec3(random.random() * scale[0], 0, random.random() * scale[2])


def randp3yz(scale=1):
    if type(scale) in (float, int):
        scale = vec3(scale)
    return glm.vec3(0, random.random() * scale[1], random.random() * scale[2])


def randp3yz(scale=1):
    if type(scale) in (float, int):
        scale = vec3(scale)
    return glm.vec3(random.random() * scale[0], random.random() * scale[1], 0)


def randp3(scale=1):
    if type(scale) in (float, int):
        scale = vec3(scale)
    return glm.vec3(
        random.random() * scale[0],
        random.random() * scale[1],
        random.random() * scale[2],
    )


def randv3xz(scale=1):
    return glm.normalize(glm.vec3(nrand(), 0, nrand())) * scale


def randv3yz(scale=1):
    return glm.normalize(glm.vec3(0, nrand(), nrand())) * scale


def randv3xy(scale=1):
    return glm.normalize(glm.vec3(nrand(), nrand(), 0)) * scale


random_direction_2D = randv3xy


def randv3(scale=1):
    return glm.normalize(glm.vec3(nrand(), nrand(), nrand())) * scale


def random_direction_2D(speed=1):
    return randv3xy(speed)


def random_direction_3D(speed=1):
    return randv3(speed)


def randb():
    return random.getrandbits(1)


def nrandb():
    return 1 if random.getrandbits(1) else -1


def randf(*args):
    """
    Random float value in range [args[0], args[1]]
    Or: random float value, scaled 
    """
    lenargs = len(args)
    if lenargs == 0:
        return random.random()
    elif lenargs == 1:
        return randf((0, args[0]))
    return args[0] + random.random() * (args[1] - args[0])


def nrand(*args):
    """
    Random float in range [-1,1]
    Or: Random float in range [-s, s]
    Or: Random float in range [-args[0], args[1]]
    """
    lenargs = len(args)
    if lenargs == 0:
        return randf(-1, 1)
    elif lenargs == 1:
        return randf(-args[0], args[0])  # 0 0 one arg = range scale
    elif lenargs == 2:
        return randf(-args[0], args[1])  # 0 1 two args = range start/end

    assert False


nrandf = nrand


def ncolor(s=1):
    return vec4(randv3(), 1.0)


def nbool(s=1):
    """
    Converts bool to -1 or 1 based on False or True.
    Scalable by speciying `s`
    """
    return s if b else -s


def deadzone(f, dz=0.5):
    """
    map a value from a normalized range to one with a deadzone radius dz
    Values from the deadzone edge and up with will be (0,1)
    """
    if type(f) == float:
        if f <= d:
            return 0
        return sign(f) * map_range(abs(f), (dz, 1), (0, 1))

    assert False  # not yet impl


def frange(start, stop=None, step=1.0):
    """
    Floating-point range(), beware of float precision
    range(5) -> 0, 1, 2, 3, 4 (f)
    range(2,5) -> 2, 3, 4 (f)
    range(5,1,-1) -> 5, 4, 3, 2 (f)
    """
    if stop is None:
        stop = start
        start = 0.0

    count = 0
    f = start
    assert glm.sign(stop - start) == glm.sign(step)
    while f < stop:
        yield f
        f += step
        count += 1


def to_deg(self, turns):
    """
    Converts turns to degrees
    """
    return turns * 360.0


def deg(self, deg):
    """
    Converts degrees to turns
    """
    return d / 360.0


def to_rad(self, turns):
    """
    Converts turns to radians
    """
    return turns * math.tau


def rad(self, rad):
    """
    Converts radians to turns
    """
    return rad / math.tau


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


def walk(obj):
    """
    Recursive iterator w/ fallback
    TODO: Add more type support
    """
    try:
        func = obj.walk
    except AttributeError:
        func = None
    
    if func:
        return func()
    # try:
    #     return obj.__walk__()
    # except AttributeError:
    #     pass

    return iter(obj)

# turn-based trig funcs

def sint(t):
    return math.sin(t * math.tau)
def cost(t):
    return math.cos(t * math.tau)
def tant(t):
    return math.tan(t * math.tau)

def asint(t):
    return math.asin(t) / math.tau
def acost(t):
    return math.acos(t) / math.tau
def atant(t):
    return math.atan(t) / math.tau

# FlowControl = enum.Enum("FlowControl", "continue skip repeat restart break exit")

VEC3ZERO = glm.vec3(0)
M = glm.mat4

# class classproperty:
#     def __init__(self, func):
#         self.func = func
#     def __get__(self, instance, cls):
#         return self.func(cls)
