#!/usr/bin/env python

import glm
from enum import Enum

# buttons
LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
JUMP = 4
CROUCH = 5
USE = 7
TURN_LEFT = 8
TURN_RIGHT = 9
MAX_BUTTONS = 10

Space = Enum("Space", "LOCAL PARENT WORLD")

LOCAL = Space.LOCAL
PARENT = Space.PARENT
WORLD = Space.WORLD

EPSILON = 0.00001


def V(*args):
    lenargs = len(args)
    if lenargs == 2:
        return glm.vec2(*args)
    elif lenargs == 4:
        return glm.vec4(*args)
    return glm.vec3(*args)


X = glm.vec3(1, 0, 0)
XY = glm.normalize(glm.vec3(1, 1, 0))
Y = glm.vec3(0, 1, 0)
YZ = glm.normalize(glm.vec3(0, 1, 1))
Z = glm.vec3(0, 0, 1)
XZ = glm.normalize(glm.vec3(1, 0, 1))

nXY = glm.normalize(glm.vec3(-1, 1, 0))
nYZ = glm.normalize(glm.vec3(0, -1, 1))
XnY = glm.normalize(glm.vec3(1, -1, 0))
nYZ = glm.normalize(glm.vec3(0, -1, 1))
YnZ = glm.normalize(glm.vec3(0, 1, -1))
nXZ = glm.normalize(glm.vec3(-1, 0, 1))
XnZ = glm.normalize(glm.vec3(1, 0, -1))

# For others use:
#  -X, -Y, -Z, -XY, -YZ, -XZ, etc.

AXIS = (X, Y, Z)
