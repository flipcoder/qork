#!/usr/bin/env python

from .reactive import Reactive, Lazy, WeakLambda
from .indexlist import IndexList
from glm import ivec2
from .easy import qork_app


class CoreBase:
    pass


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


def get_function_from_args(args, kwargs=None):
    func = None
    if not args:
        return None
    for arg in args:  # check first non-app arg for func
        if callable(arg):
            func = arg
            break
        if not isinstance(arg, CoreBase):
            break
    if not func and kwargs:  # if no func, look it up in kwargs
        func = kwargs.get("func", None)
    return func


class MinimalCore(CoreBase):
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

        # create and enable default profile
        from .profile import Profile

        profile = Profile(self, default=True)
        profile.enable()
        self.default_profile = profile
        self.default_profile_idx = 0

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
        # if self.profiles:
        #     for prof in self.profiles.safe_iter():
        #         prof.update(dt)
        if self.controllers:
            for ctrl in self.controllers.safe_iter():
                ctrl.update(dt)

    @property
    def partitioner(self):
        return self._partitioner


class StateBase:
    def update(self, dt):
        pass
