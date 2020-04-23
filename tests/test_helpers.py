#!/usr/bin/env pytest


class Counter:
    def __init__(self, x=0):
        self.x = x

    def increment(self, v=None):
        # print("inc ", v)
        if v is not None:
            self.x += v
            return
        self.x += 1

    def __call__(self):
        return self.x

