#!/usr/bin/python
from .node import *
from .reactive import *
import glm
import math

class Camera(Node):
    def __init__(self, app=None, **kwargs):
        super().__init__(app, **kwargs)
        self.ortho = Reactive(False)
        self.projection = Lazy(lambda self=self: glm.perspectiveFov(
            math.radians(self._fov()),
            float(self.app.window_size[0]),
            float(self.app.window_size[1]),
            0.1, 1000.0
        ), [self.ortho])
        self.app.on_resize.connect(self.projection.pend, 'camera')
        self._fov = Reactive(80.0, [self.projection.pend])
        self.view = Lazy(
            lambda self=self: glm.inverse(self.matrix(WORLD)),
            [self.on_pend]
        )
        self.view_projection = Lazy(
            lambda self=self: self.projection() * self.view(),
            [self.projection, self.view],
        )
    @property
    def fov(self):
        return self._fov()
    @fov.setter
    def fov(self, v):
        self._fov(v)

    def cleanup():
        self.app.on_resize.disconnect('camera')

