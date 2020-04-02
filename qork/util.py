#!/usr/bin/env python

import itertools
import types
import glm
from functools import reduce
import operator
import random
from .defs import *


class Dummy:
    pass


DUMMY = Dummy()


class Wrapper:
    def __init__(self, value=None):
        self.value = value

    def __call__(self, value=Dummy()):
        if type(value) == Dummy:
            return self.value
        self.value = value
        return value

    def do(self, func):
        self.value = func(self.value)
        return self.value


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
    assert type(a) == type(b)
    if type(a) == float:
        return abs(a - b) < EPSILON
    else:
        for c in range(len(a)):
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
    if isinstance(args[0], tuple) or isinstance(args[0], list):
        args = args[0]
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
        elif lenargs == 1:
            return glm.vec3(args[0])
        elif lenargs == 2:
            return glm.vec3(*args, 0)
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


def randv3(scale=1):
    return glm.normalize(glm.vec3(nrand(), nrand(), nrand())) * scale


def randf(s=1):
    return random.random() * s


def nrand(s=1):
    return (random.random() * 2 - 1) * s


def ncolor(s=1):
    return vec4(randv3(), 1.0)


M = glm.mat4

# class classproperty:
#     def __init__(self, func):
#         self.func = func
#     def __get__(self, instance, cls):
#         return self.func(cls)
