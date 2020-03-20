#!/usr/bin/env python

from .easymode import qork

class Resource:
    def __init__(self, *args, **kwargs):
        if not args or isinstance(args[0], str):
            self.app = qork()
            self.cache = None
            if self.app:
                self.cache = self.app.cache
        self.args = args
        self.kwargs = kwargs
    def cleanup(self):
        pass

