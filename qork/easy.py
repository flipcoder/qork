#!/usr/bin/python

from collections import defaultdict
from qork.signal import Signal
from qork.reactive import *

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
    return APP.add(*args, **kwargs)


def find(*args, **kwargs):
    return APP.world.find(*args, **kwargs)


def find_one(*args, **kwargs):
    return APP.world.find(*args, one=True, **kwargs)


def remove(*args, **kwargs):
    return APP.remove(*args, **kwargs)


def create(*args, **kwargs):
    return APP.create(*args, **kwargs)


def clear():
    return APP.scene.clear()


# def music(fn):
#     return APP.add(fn, loop=True)
