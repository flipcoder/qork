#!/usr/bin/env python

import numpy as np
import glm

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

class Prefab:
    def __init__(self, *args):
        lenargs = len(args)
        if lenargs > 1:
            self.name = args[0]
            self.data = args[1]
        else:
            self.name = ''
            self.data = args[0]

QUAD = Prefab('QUAD', np.array([
#     x    y    z
    0.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
]))

QUAD_CENTERED = Prefab('QUAD_CENTERED', np.array([
#      x    y    z
    -1.0, -1.0,  0.0,
     1.0, -1.0,  0.0,
    -1.0,  1.0,  0.0,
     1.0,  1.0,  0.0,
]))

TEXTURED_QUAD_CENTERED = Prefab('TEXTURED_QUAD_CENTERED', np.array([
#      x     y    z    u    v
    -0.5, -0.5, 0.0, 0.0, 1.0,
     0.5, -0.5, 0.0, 1.0, 1.0,
    -0.5,  0.5, 0.0, 0.0, 0.0,
     0.5,  0.5, 0.0, 1.0, 0.0
]))


TEXTURED_QUAD = Prefab('TEXTURED_QUAD', np.array([
#     x    y    z    u    v
    0.0, 0.0, 0.0, 0.0, 1.0,
    1.0, 0.0, 0.0, 1.0, 1.0,
    0.0, 1.0, 0.0, 0.0, 0.0,
    1.0, 1.0, 0.0, 1.0, 0.0,
]))

X = glm.vec3(1,0,0)
Y = glm.vec3(0,1,0)
Z = glm.vec3(0,0,1)

