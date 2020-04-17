#!/usr/bin/env python

import moderngl_window as mglw
from .easy import qork_app
from .util import *


class Resource:
    def __init__(self, *args, **kwargs):
        self.fn = filename_from_args(args, kwargs)
        if not args or not isinstance(args[0], mglw.WindowConfig):
            self.app = qork_app()
            self.cache = None
            if self.app:
                self.cache = self.app.cache
        else:
            self.app = args[0]
        self.args = args
        self.kwargs = kwargs

    @property
    def count(self):
        return self.cache.count(self) - 1

    def cleanup(self):
        pass
