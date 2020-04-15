#!/usr/bin/python

from qork import Node
from qork import easy

# Decorators
def overlap(a, b):
    """
    Overlap continuous collision callback
    Function shold be in the form (a, b, t)
    """

    def overlap_decorator(func):

        if not isinstance(a, Node):
            for aa in a:
                overlap(aa, b)(func)
            return func

        if not isinstance(b, Node):
            for bb in b:
                overlap(a, bb)(func)
            return func

        easy.qork_app().overlap[a][b] += func
        return func

    return overlap_decorator


# def call(func):
#     func()
#     return func


def on_update(func, context=None):
    context = context or easy.qork_app()
    return func


def when(cond, context=None, lifespan=None, **kwargs):
    """
    auto-schedule a When condition in the current context
    :param context: where to listen for event
    :param lifespan: object that holds event connection
    """

    context = context or easy.qork_app()

    def decorator(func):
        global lifespan
        slot = context.when(cond, func, weak=lifespan, **kwargs)
        if lifespan:
            lifespan.connections += slot
        func._when_slot = slot
        return func

    return decorator
