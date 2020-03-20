#!/usr/bin/env python

import numpy as np

# buttons
LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
JUMP = 4
CROUCH = 5
TURN_LEFT = 6
TURN_RIGHT = 7
MAX_BUTTONS = 8

# space
LOCAL = 0
PARENT = 1
WORLD = 2

EPSILON = 0.00001

QUAD = ('QUAD', np.array([
#     x    y    z
    0.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
]))

QUAD_CENTERED = ('QUAD_CENTERED', np.array([
#      x    y    z
    -1.0, -1.0,  0.0,
     1.0, -1.0,  0.0,
    -1.0,  1.0,  0.0,
     1.0,  1.0,  0.0,
]))

TEXTURED_QUAD_CENTERED = ('TEXTURED_QUAD_CENTERED', np.array([
#      x     y    z    u    v
    -0.5, -0.5, 0.0, 0.0, 1.0,
     0.5, -0.5, 0.0, 1.0, 1.0,
    -0.5,  0.5, 0.0, 0.0, 0.0,
     0.5,  0.5, 0.0, 1.0, 0.0
]))


TEXTURED_QUAD = ('TEXTURED_QUAD', np.array([
#     x    y    z    u    v
    0.0, 0.0, 0.0, 0.0, 1.0,
    1.0, 0.0, 0.0, 1.0, 1.0,
    0.0, 1.0, 0.0, 0.0, 0.0,
    1.0, 1.0, 0.0, 1.0, 0.0,
]))

