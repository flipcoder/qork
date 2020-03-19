#!/usr/bin/env python

import itertools
import types
import glm
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

def filename(*args, **kwargs):
    fn = None
    for arg in args: # check args for filename (first string
        if isinstance(arg, str):
            fn = arg
            break
    if not fn: # if no filename, look it up in kwargs
        fn = kwargs.get('fn') or kwargs.get('filename') 
    return fn

def fcmp(a, b):
    assert type(a) == type(b)
    if type(a) == float:
        return abs(a - b)  < EPSILON
    else:
        for c in range(len(a)):
            if abs(a[c] - b[c]) >= EPSILON:
                return False
        return True

