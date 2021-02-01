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
    
    return app

class MinimalCore:
    """
    Core base class that does the minimal amount for testing purposes.
    Used both as a base and a mock app.
    """

    def __init__(self):
        self.cache = None
        self.ctx = None
        self._size = Reactive(ivec2(1920, 1080))
        self.cameras = IndexList()
        self.profiles = IndexList()
        self.controllers = IndexList()
        self._partitioner = None
        self.session = None

    # def plug(self, ctrl):
    #     self.controllers += ctrl
    # def unplug(self, ctrl):
    #     self.controllers -= ctrl

    def create(self, *args, **kwargs):
        from .node import Node

        return Node(*args, **kwargs)

    def register_camera(self, camera):
        if camera.camera_id is None:
            camera.camera_id = self.cameras.add(camera)

    def deregister_camera(self, camera):
        if camera is not None and camera.camera_id is not None:
            self.cameras.remove(camera.camera_id)

    def update(self, dt):
        self.session.update(dt)
        if self.profiles:
            for prof in safe_iter(self.profiles):
                prof.update(dt)
        if self.controllers:
            for ctrl in safe_iter(self.controllers):
                ctrl.update(dt)

    @property
    def partitioner(self):
        return self._partitioner

class StateBase:
    def update(self, dt):
        pass

