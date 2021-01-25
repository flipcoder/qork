#!/usr/bin/env python

import moderngl_window as mglw
import pathlib
from .easy import qork_app
from .util import *
from .signal import Connections


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
        self.connections = Connections()

    # @property
    # def count(self):
    #     return self.cache.count(self) - 1

    def cleanup(self):
        pass

    def get(self):
        """
        Gets the underlying resource, used for proxy resources
        """
        return self

    def update(self, dt):
        pass

    def __iadd__(self, con):
        self.connections += con
        return self

    def __isub__(self, con):
        self.connections -= con
        return self


# example: a textured quad model which shares the underlying
class ResourceInstance(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rc = None

    def update(self, dt):
        pass

    def get(self):
        return self.rc
