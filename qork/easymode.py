#!/usr/bin/python

APP = None
CACHE = None

def qork(a=None):
    global APP
    if a==None:
        return APP
    APP = a
    return APP
def load(*args):
    global CACHE
    if len(args) == 0:
        return CACHE
    if CACHE is not None: # cache is already defined? call it
        return CACHE(*args)
    CACHE = args[0]
    return CACHE
def add(node):
    return qork().add(node)
cache = load

