#!/usr/bin/env python

from .signal import Signal
from glm import vec3


class Box:
    def __init__(self):
        self.region = [vec3(0), vec3(0)]
        self.on_pend = Signal()
        self.on_change = Signal()

    def __getitem__(self, i):
        return self.region[i]

    def __setitem__(self, i, v):
        self.region[i] = vec3(*v)
        self.on_change(v)
        self.on_pend(v)

    def __iadd__(self, arg):
        if callable(arg):  # function?
            # params = len(inspect.signature(v).parameters)
            # if params:
            #     self.on_change += v
            # else:
            self.on_pend += arg
        elif isinstance(v, Box):
            raise Exception("Box.iadd(Box) not yet impl")
            # combine boxes

        # assume point?
        arg = to_vec3(arg)
        raise Exception("Box.iadd(vec3) not yet impl")

    def min(self):
        return self.region[0]

    def max(self):
        return self.region[1]

    def size(self):
        return self.region[1] - self.region[0]

    def __bool__(self):
        for c in self.size():
            if c < EPSILON:
                return False
        return True
