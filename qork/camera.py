#!/usr/bin/python
from .node import *
import glm
import math

class Camera(Node):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        fov = 80.0
        self.projection = glm.perspectiveFov(
            math.radians(fov), 960.0, 540.0, 0.1, 1000.0
        )

