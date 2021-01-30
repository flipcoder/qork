#!/usr/bin/env python

from .reactive import Reactive, Lazy, WeakLambda
from .indexlist import IndexList
from glm import ivec2
from .easy import qork_app


def get_app_from_args(args):
    app = None
    if args:
        arg0 = args[0]

        if isinstance(arg0, MinimalCore):
            app = arg0
        else:
            app = qork_app()
    else:
        app = qork_app()

    if app is None:
        app = MinimalCore()


class MinimalCore:
    """
    Core base class that does the minimal amount for testing purposes.
    Similar to a mock app.
    """

    def __init__(self):
        self.cache = None
        self.ctx = None
        self.partitioner = None
        self._size = Reactive(ivec2(1920, 1080))
        self.cameras = IndexList()

    def create(self, *args, **kwargs):
        from .node import Node

        return Node(*args, **kwargs)

    def register_camera(self, camera):
        if camera.camera_id is None:
            camera.camera_id = self.cameras.add(camera)

    def deregister_camera(self, camera):
        if camera is not None and camera.camera_id is not None:
            self.cameras.remove(camera.camera_id)

class StateBase:
    def update(self, dt):
        pass

