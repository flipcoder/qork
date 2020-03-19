#!/usr/bin/env python

import itertools
import types

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

