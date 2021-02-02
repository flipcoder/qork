#!/usr/bin/env pytest
import pytest
import sys

sys.path.append("..")

from qork.util import fcmp
from qork.box import Box
from glm import vec3


def test_box():
    box = Box()
    assert fcmp(box.min, vec3(0))
    assert fcmp(box.max, vec3(0))

    box = Box(low=[1, 2, 3], high=[4, 5, 6])
    assert fcmp(box.min, [1, 2, 3])
    assert fcmp(box.max, [4, 5, 6])


def test_box_overlap():
    box = Box()
    abox = Box(high=[1.1, 2.2, 3.3])
    bbox = Box(low=[1, 2, 3], high=[4, 4, 4])
    assert abox.overlap(bbox)  # collision


def test_box_intersect():
    box = Box()
    abox = Box(high=[1.1, 2.2, 3.3])
    bbox = Box(low=[1, 2, 3], high=[4, 4, 4])

    intersection = abox.intersect(bbox)
    assert fcmp(intersection.min, [1, 2, 3])
    assert fcmp(intersection.max, [1.1, 2.2, 3.3])
    assert fcmp(intersection.size(), [0.1, 0.2, 0.3])

    abox = Box(high=1)
    bbox = Box(low=2, high=3)
    assert not abox.overlap(bbox)
    intersection = abox.intersect(bbox)
    assert fcmp(intersection.min, vec3(0))
    assert fcmp(intersection.max, vec3(0))
    assert fcmp(intersection.size(), vec3(0))
