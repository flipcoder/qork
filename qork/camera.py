#!/usr/bin/python
from .node import *
import glm
import math

class Camera(Node):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        fov = 80.0
        self.projection = glm.perspectiveFov(
            math.radians(fov),
            float(self.app.window_size[0]),
            float(self.app.window_size[1]),
            0.1, 1000.0
        )

