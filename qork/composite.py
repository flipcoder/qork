#!/usr/bin/env python

from types import MethodType
import functools

from .signal import Container


class CompositeBase(Container):
    def __init__(self, *args, **kwargs):
        super().__init__()


def Composite(*args):
    if not args:
        return CompositeBase

    args = list(args)

    class CompositeClass(CompositeBase):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self += args  # container add all instances in args

        # def do(self, func, *args):
        #     for n in self:
        #         func(*args)

    # List of types used in composite
    types = set()
    for obj in args[:]:
        if type(obj) == type:
            types.add(obj)
            args.remove(obj)
        else:
            types.add(type(obj))

    for typ in types:
        for name, func in typ.__dict__.items():
            if name.startswith("__"):
                continue
            print(name, func)

            def composite_method(self, *a, **k):
                r = [None] * len(self)
                for i, e in enumerate(self):
                    r[i] = func(e, *a, **k)
                return r

            # def bind(instance, method):
            #     def binding_scope_func(*args, **kwargs):
            #         return method(instance, *args, **kwargs)
            #     return binding_scope_func
            setattr(CompositeClass, name, composite_method)

    if len(args) == 0:
        # all types and no instances?
        # This means it's basically a Mixin class
        return CompositeClass

    return CompositeClass(*args)
