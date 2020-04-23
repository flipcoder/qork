#!/usr/bin/python

from qork import Node
from qork import easy

# Decorators
def overlap(a, b=None):
    """
    Overlap continuous collision callback
    Function shold be in the form (a, b, t)
    where a and b are objects, classes, or node names
    """

    if b is None:
        b = a # same name or type
    
    def overlap_decorator(func):
        
        if type(a) in (tuple, list):
            for aa in a:
                overlap(aa, b)(func)
            return func

        if type(b) in (tuple, list):
            for bb in b:
                overlap(a, bb)(func)
            return func

        easy.qork_app().partitioner.overlap[a][b] += func
        return func

    return overlap_decorator


def callnow(func):
    func()
    return func


# def on_update(func, context=None):
#     context = context or easy.qork_app()
#     return func

def call_every(duration, context=None, lifespan=None, **kwargs):
    
    context = context or easy.qork_app()

    def every_decorator(func):
        slot = context.when.every(duration, func, weak=bool(lifespan), **kwargs)
        if lifespan:
            lifespan.connections += slot
        func._when_slot = slot
        return func

    return every_decorator

def call_once(duration, context=None, lifespan=None, **kwargs):
    return every(duration, context, lifespan, once=True, *kwargs)

def call_when(cond, context=None, lifespan=None, **kwargs):
    """
    auto-schedule a When condition in the current context
    :param context: where to listen for event
    :param lifespan: object that holds event connection
    """

    context = context or easy.qork_app()

    def when_decorator(func):
        slot = context.when(cond, func, weak=bool(lifespan), **kwargs)
        if lifespan:
            lifespan.connections += slot
        func._when_slot = slot
        return func

    return when_decorator

