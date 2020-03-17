#!/usr/bin/python
from node import *
import glm

class Camera(Node):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.projection = glm.perspectiveFov(
            90.0, 800.0, 600.0, 0.0, 100.0
        )

