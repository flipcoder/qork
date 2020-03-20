#!/usr/bin/env python

class Resource:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def cleanup(self):
        pass

