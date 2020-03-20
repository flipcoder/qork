#!/usr/bin/python
from .node import *
from .reactive import *
import glm
import math

class Camera(Node):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self._fov = 80.0
        self.projection = Lazy(lambda self=self: glm.perspectiveFov(
            math.radians(self._fov),
            float(self.app.window_size[0]),
            float(self.app.window_size[1]),
            0.1, 1000.0
        ))
        self.view = Lazy(lambda self=self: glm.inverse(self.matrix(WORLD)))
        self.view_projection = Lazy(
            lambda self=self: self.projection() * self.view(),
            [self.projection, self.view, self.app.on_resize]
        )
        self.app.on_resize.connect(self.projection.pend, 'camera')
        self.on_pend.connect(self.view.pend)
    
    @property
    def fov(self):
        return self._fov
    
    @fov.setter
    def fov(self, v):
        self._fov = v
        self.projection.pend()

    def cleanup():
        self.app.on_resize.disconnect('camera')

