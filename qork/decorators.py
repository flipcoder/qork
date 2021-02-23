#!/usr/bin/python

from qork import Node
from qork import easy

# Decorators
def collision(event, a, b=None):
    """
    Continuous collision callback
    Function shold be in the form (a, b, t)
    where a and b are objects, classes, or node names
    `event` is string representation of the Partitioner.CollisionEvent
        (overlap, apart, enter or leave)
    """

    if b is None:
        b = a  # same name or type

    def collision_decorator(func):

        if type(a) in (tuple, list):
            for aa in a:
                collision(event, aa, b)(func)
            return func

        if type(b) in (tuple, list):
            for bb in b:
                collision(event, a, bb)(func)
            return func

        # does a or b have a specific handler?
        ac, bc = None, None
        try:
            ac = a.collision_handler
        except AttributeError:
            pass
        try:
            bc = b.collision_handler
        except AttributeError:
            pass
        if ac or bc:
            assert not (ac and bc)  # both objects are collsion handlers?
            if ac:

                def collision_handler(*args, **kwargs):
                    if a.handle_collision(b):
                        func(a, b)

            else:  # bc

                def collision_handler(*args, **kwargs):
                    if b.handle_collision(a):
                        func(b, a)

            easy.qork_app().state_scene.partitioner.register_callback(event, a, b, collision_handler)
        else:
            easy.qork_app().state_scene.partitioner.register_callback(event, a, b, func)
        return func

    return collision_decorator


def collision_overlap(self, a, b=None):
    return collision('overlap', a, b)
# def collision_apart(self, a, b=None):
#     return collision('apart', a, b)
def collision_enter(self, a, b=None):
    return collision('enter', a, b)
def collision_leave(self, a, b=None):
    return collision('leave', a, b)

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


def delay(duration, context=None, lifespan=None, **kwargs):
    return call_every(duration, context, lifespan, once=True, *kwargs)


call_once = delay


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


def coro(context=None, lifespan=None):
    context = context or easy.qork_app()

    def coro_decorator(func):
        slot = context.add_script(func, weak=(lifespan is not None))

        if lifespan is not None:
            lifespan.connections += slot
        return func

    return coro_decorator
