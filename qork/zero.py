#!/usr/bin/python

APP = None

def qork_app(a=None):
    global APP
    if a is None:
        return APP
    APP = a
    return APP
def cache(*args, **kwargs):
    return APP.cache(*args, **kwargs)
def add(*args, **kwargs):
    return APP.add(APP.Entity(*args, **kwargs))
# def remove(node, *kwargs):
#     return node.remove_if((lambda n: n==node), **kwargs)

