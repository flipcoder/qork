#!/usr/bin/env pytest

import sys

sys.path.append("..")

from qork.minimal import MinimalCore
from qork.camera import Camera
from qork.easy import qork_app


def test_camera_register():
    app = MinimalCore()
    assert len(app.cameras.container) == 0
    cam = Camera(app)
    assert len(app.cameras.container) == 1
    cam2 = Camera(app)
    assert len(app.cameras.container) == 2
    app.deregister_camera(cam)
    assert len(app.cameras.container) == 2  # no resize
    assert app.cameras.container[0] == None
