#!/usr/bin/env python

import moderngl_window as mglw
import pathlib
from .easy import qork_app
from .util import *
from .signal import Connections
from .minimal import get_app_from_args
from .util import get_subpath


class Resource:
    def __init__(self, *args, **kwargs):
        self.dead = False
        self.use_refs = False
        self.refs = 0

        self.fn = filename_from_args(args, kwargs)
        self.app = get_app_from_args(args)
        self.cache = self.app.cache

        try:
            self.flags = os.path.basename(self.fn).split(":")[0].split("+")[1:]
        except:
            self.flags = []

        # print(type(self).__name__)

        self.subpath = get_subpath(self.fn)
        self.fn = remove_subpath(self.fn)

        if self.fn:
            self.ext = pathlib.Path(self.fn).suffix
        else:
            self.ext = ""
        if self.fn:
            self.full_fn = self.app.resource_path(self.fn)
        else:
            self.full_fn = None

        self.args = args
        self.kwargs = kwargs
        self.connections = Connections()

    # @property
    # def count(self):
    #     return self.cache.count(self) - 1

    def cleanup(self):
        if not self.dead:
            self.refs = 0
            self.dead = True

    def ref(self, count=1):
        self.use_refs = True
        r = self.refs
        self.refs += count
        return r

    def deref(self, count=1):
        self.refs -= count
        refs = self.refs
        if refs == 0:
            # TODO: push cleanup into scheduler
            self.cleanup()

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

    def __del__(self):
        self.cleanup()


# example: a textured quad model which shares the underlying resource?
# is this even used anymore?
class ResourceInstance(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rc = None

    def update(self, dt):
        pass

    def get(self):
        return self.rc
