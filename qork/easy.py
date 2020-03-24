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
    return APP.add(*args, **kwargs)


def create(*args, **kwargs):
    return APP.create(*args, **kwargs)


# QORK_SCRIPT = False
# def qork_script(self, *args):
#     global QORK_SCRITP
#     if not args:
#         return QORK_SCRIPT
#     QORK_SCRIPT = bool(args[0])
#     return QORK_SCRIPT

# def remove(node, *kwargs):
#     return node.remove_if((lambda n: n==node), **kwargs)
