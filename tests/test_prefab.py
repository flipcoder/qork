#!/usr/bin/env pytest
import sys

sys.path.append("..")

from qork.defs import *
from qork.prefab import *
from qork.box import *

# fmt: off

def test_quad():
    assert prefab_quad() == [
        0.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 1.0, 0.0,
        1.0, 1.0, 0.0,
        1.0, 0.0, 0.0
    ]

def test_center_quad():
    assert prefab_quad('c', z=2.0) == [
        -0.5, -0.5, 2.0,
         0.5, -0.5, 2.0,
        -0.5,  0.5, 2.0,
        -0.5,  0.5, 2.0,
         0.5, -0.5, 2.0,
         0.5,  0.5, 2.0,
    ]

def test_textured_quad():
    assert prefab_quad('ct', z=3.0) == [
        -0.5, -0.5, 3.0, 0.0, 1.0,
         0.5, -0.5, 3.0, 1.0, 1.0,
        -0.5,  0.5, 3.0, 0.0, 0.0,
        -0.5,  0.5, 3.0, 0.0, 0.0,
         0.5, -0.5, 3.0, 1.0, 1.0,
         0.5,  0.5, 3.0, 1.0, 0.0,
    ]

# fmt: on
