#!/usr/bin/env pytest
import sys

sys.path.append("..")

from qork.defs import *
from qork.box import *

def test_quad():
    assert quad() == [
        0.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        1.0, 1.0, 0.0
    ]

def test_center_quad():
    assert quad('c', z=2) == [
        -1.0, -1.0,  2.0,
         1.0, -1.0,  2.0,
        -1.0,  1.0,  2.0,
         1.0,  1.0,  2.0,
    ]

def test_textured_quad():
    assert quad('c', z=3) == [
        -0.5, -0.5, 3.0, 0.0, 1.0,
         0.5, -0.5, 3.0, 1.0, 1.0,
        -0.5,  0.5, 3.0, 0.0, 0.0,
         0.5,  0.5, 3.0, 1.0, 0.0
    ]

