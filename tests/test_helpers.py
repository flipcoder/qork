#!/usr/bin/env python


class Counter:
    def __init__(self):
        self.x = 0

    def increment(self, v=None):
        print("inc ", v)
        if v is not None:
            self.x += v
            return
        self.x += 1


class Wrapper:
    pass
