#!/usr/bin/env python

import itertools
import types
import glm
from functools import reduce
import operator
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
    return isinstance(func, types.LambdaType) and \
        func.__name__ == '<lambda>'

def flatten(r):
    return tuple(itertools.chain(*r))

def filename_from_args(args, kwargs=None):
    fn = None
    if not args:
        return None
    for arg in args: # check args for filename (first string)
        if isinstance(arg, str):
            fn = arg
            break
    if not fn and kwargs: # if no filename, look it up in kwargs
        fn = kwargs.get('fn') or kwargs.get('filename') or ''
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

def isinstance_any(e, types):
    for t in types:
        if isinstance(e, t):
            return True
    return False

def recursive_each(types, e, func, path=[]):
    if type(types) == type:
        types = [types]
    if isinstance_any(e, types):
        func(e, path)
    elif isinstance(e, dict):
        for key, child in e.items():
            recursive_each(types, child, func, path + [key])
    elif isinstance(e, list):
        for i in range(len(e)):
            recursive_each(types, e[i], func, path + [i])

def to_vec3(*args):
    # lenargs = len(args)
    if isinstance(args[0], tuple) or isinstance(args[0], list):
        args = args[0]
    if isinstance(args, glm.vec3):
        return args
    elif isinstance(args, glm.vec2):
        return glm.vec3(args, 0.0)
    elif isinstance(args, glm.vec4):
        return args.xyz
    return glm.vec3(*args)

V = to_vec3
M = glm.mat4

# class classproperty:
#     def __init__(self, func):
#         self.func = func
#     def __get__(self, instance, cls):
#         return self.func(cls)

