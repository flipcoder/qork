#!/usr/bin/python

from qork import Node
from qork import easy

# Decorators

# def overlap(a, b):
#     def overlap_decorator(func):

#         if not isinstance(a, Node):
#             for aa in a:
#                 overlap(aa, b)
#                 return func

#         if not isinstance(b, Node):
#             for bb in b:
#                 overlap(a, bb)
#                 return func

#         try:
#             overlapA = APP.overlap[id(a)]
#         except KeyError:
#             overlapA = APP.overlap = defaultdict(Signal)

#         overlapA[id(b)] += func
#         return func
#     return overlap_decorator

# Decorators


def overlap(a, b):
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


# class A:
#     @scoped
#     def hi(self):
#         print('hi')
#     pass

# def scoped(func):
#     def scoped_func(self, *args):
#         func(self.scope, *args)
#     return scoped_func
