#!/usr/bin/env pytest

import sys

sys.path.append("..")
from qork.partitioner import Partitioner
from qork.scene import Scene
from qork.node import Node
from qork.box import Box
from test_helpers import *
from glm import vec4


def test_overlap():
    counter = Counter()
    scene = Scene()
    partitioner = scene.partitioner
    a = scene.add(Node(scene.app))
    b = scene.add(Node(scene.app))
    partitioner.register_callback("overlap", a, b, lambda a, b, dt: counter.increment)
    a.set_local_box(Box(low=0, high=1))
    a.set_local_box(Box(low=2, high=3))
    scene.update(0.1)
    assert counter() == 0

    a.set_local_box(Box(low=0, high=4))
    b.set_local_box(Box(low=2, high=3))
    scene.update(0.1)
    assert counter() == 1
