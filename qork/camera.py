#!/usr/bin/python
from .node import *
from .reactive import *
import glm
import math


class Camera(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ortho = Reactive(False)
        self._mode = Reactive("3D")
        self.projection = Lazy(self.calculate_projection, [self.ortho, self._mode])
        self.slots = []
        self.slots.append(self.app.on_resize.connect(self.projection.pend))
        self._fov = Reactive(80.0, [self.projection.on_pend])
        self.view = Lazy(lambda self=self: glm.inverse(self.matrix(WORLD)), [self])
        self.view_projection = Lazy(
            lambda self=self: self.projection() * self.view(),
            [self.projection, self.view],
        )

    def calculate_projection(self):
        if self.mode == "3D":
            return glm.perspectiveFov(
                math.radians(self._fov()),
                float(self.app.window_size[0]),
                float(self.app.window_size[1]),
                0.1,
                1000.0,
            )
        elif self.mode == "2D":
            return glm.mat4(1)
        else:
            assert False

    @property
    def fov(self):
        return self._fov()

    @fov.setter
    def fov(self, v):
        self._fov(v)

    @property
    def mode(self):
        return self._mode()

    @mode.setter
    def mode(self, m):
        self._mode(m.upper())
        return m

    def cleanup():
        for slot in self.slots:
            slot.disconnect()
        self.slots = []
