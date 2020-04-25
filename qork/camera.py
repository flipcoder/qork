#!/usr/bin/python
from .node import *
from .reactive import *
import glm
import math
from enum import Enum


class Camera(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ortho = Reactive(True)
        self.projection = Lazy(
            self.calculate_projection,
            [self._ortho, self.app._size],
            [self.app.view_projection],
        )
        # self.connections += self.app.size.connect(self.projection)
        self._fov = Reactive(80 / 360, [self.projection])
        self.view = Lazy(self.calculate_view, [self.on_pend])
        self.view_projection = Lazy(
            lambda self=self: self.projection() * self.view(),
            [self.projection, self.view],
            [self.app.view_projection],
        )

        # self.connections += (
        #     self.projection.connect(self.app.view_projection.pend),
        #     self.view.connect(self.app.view_projection.pend)
        # )
        # self.connections += self.connect(self.app.view_projection.pend)

        self.app.view_projection.pend()

    # @depends(self)
    def calculate_view(self):
        return glm.inverse(self.world_matrix)

    def calculate_projection(self):
        if self.ortho:
            if min(self.app.size) <= 1:
                return glm.mat4(1)
            ratio = self.app.size[0] / self.app.size[1]
            ratio /= 2
            return glm.ortho(-ratio, ratio, -0.5, 0.5, 0.5, -0.5)
        else:
            return glm.perspectiveFov(
                math.tau * self._fov(),
                float(self.app.size[0]),
                float(self.app.size[1]),
                0.1,
                1000.0,
            )

    @property
    def fov(self):
        return self._fov()

    @fov.setter
    def fov(self, v):
        """
        FOV angle is in TURNS, not degrees or radians.
        Use fov(util.deg(d)) or fov(util.rad(r)) if you prefer.
        """
        assert 0 < v < 1 + EPSILON
        self._fov(v)

    @property
    def ortho(self):
        return self._ortho()

    @ortho.setter
    def ortho(self, b):
        self._ortho(b)
        return b

    @property
    def perspective(self):
        return not self._ortho()

    @perspective.setter
    def perspective(self, b):
        self._ortho(not b)
        return b

    @property
    def mode(self, m):
        return "2D" if self.ortho else "3D"

    @mode.setter
    def mode(self, m):
        self.ortho = m == 2 or m[0] == "2"

    def update(self, dt):
        super().update(dt)
