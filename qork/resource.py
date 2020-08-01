#!/usr/bin/env python

import moderngl_window as mglw
import pathlib
from .easy import qork_app
from .util import *


class Resource:
    def __init__(self, *args, **kwargs):
        self.fn = filename_from_args(args, kwargs)
        try:
            self.flags = self.fn.split(":")[0].split("+")[1:]
        except:
            self.flags = []
        if self.fn:
            self.ext = pathlib.Path(self.fn).suffix
        else:
            self.ext = ""
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
