#!/usr/bin/env python

from .signal import Signal
from glm import vec3
from .util import BIT, to_vec3


class Box:
    def __init__(self, low=None, high=None):
        low = to_vec3(low) or vec3(0)
        high = to_vec3(high) or vec3(0)
        self.region = [low, high]
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

    @property
    def min(self):
        return self.region[0]

    @property
    def max(self):
        return self.region[1]

    def size(self):
        return self.region[1] - self.region[0]

    def overlap(self, other):
        """
        Test if this box overlaps with a given box or vec3 point
        """
        if isinstance(other, Box): # box
            return not (
                other[0].x > self[1].x
                or other[1].x < self[0].x
                or other[0].y > self[1].y
                or other[1].y < self[0].y
                or other[0].z > self[1].z
                or other[1].z < self[0].z
            )
        else: #isinstance(other, glm.vec3): # point
            p = glm.vec3(*other) # assume its a point
            return not (
                other.x > self[1].x
                or other.x < self[0].x
                or other.y > self[1].y
                or other.y < self[0].y
                or other.z > self[1].z
                or other.z < self[0].z
            )
    
    def union(self, other):
        if not self.overlap(other):
            return Box()

        r = Box()
        vals = [0] * 4

        for c in range(3): # components x,y,z
            vals[0] = self[0][c]
            vals[1] = self[1][c]
            vals[2] = other[0][c]
            vals[3] = other[1][c]
            vals.sort()
            r[0][c]= vals[0]
            r[1][c]= vals[3]
        
        return r
        
    def intersect(self, other):
        if not self.overlap(other):
            return Box()

        r = Box()
        vals = [0] * 4

        for c in range(3): # components x,y,z
            vals[0] = self[0][c]
            vals[1] = self[1][c]
            vals[2] = other[0][c]
            vals[3] = other[1][c]
            vals.sort()
            r[0][c]= vals[1]
            r[1][c]= vals[2]
        
        return r

    def classify(self, other):
        """
        Classify the relationship between this box and another Box or point
        """
        r = 0
        if isinstance(other, Box):
            if other[0].x > self[1].x:
                r |= BIT(0)
            if other[1].x < self[0].x:
                r |= BIT(3)
            if other[0].y > self[1].y:
                r |= BIT(1)
            if other[1].y < self[0].y:
                r |= BIT(4)
            if other[0].z > self[1].z:
                r |= BIT(2)
            if other[1].z < self[0].z:
                r |= BIT(5)
        else:
            other = glm.vec3(*other)
            if other.x > self[1].x:
                r |= BIT(0)
            if other.x < self[0].x:
                r |= BIT(3)
            if other.y > self[1].y:
                r |= BIT(1)
            if other.y < self[0].y:
                r |= BIT(4)
            if other.z > self[1].z:
                r |= BIT(2)
            if other.z < self[0].z:
                r |= BIT(5)
        return r

    def __bool__(self):
        for c in self.size():
            if c < EPSILON:
                return False
        return True
