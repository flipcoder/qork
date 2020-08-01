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

# space
LOCAL = 0
PARENT = 1
WORLD = 2

EPSILON = 0.00001


def V(*args):
    lenargs = len(args)
    if lenargs == 2:
        return glm.vec2(*args)
    elif lenargs == 4:
        return glm.vec4(*args)
    return glm.vec3(*args)


class Prefab:
    def __init__(self, *args):
        lenargs = len(args)
        if lenargs > 1:
            self.name = args[0]
            self.data = args[1]
        else:
            self.name = ""
            self.data = args[0]


# fmt: off

QUAD = Prefab('QUAD', [
#     x    y    z
    0.0, 0.0, 0.0,
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    1.0, 1.0, 0.0,
])

QUAD_CENTERED = Prefab('QUAD_CENTERED', [
#      x    y    z
    -1.0, -1.0,  0.0,
     1.0, -1.0,  0.0,
    -1.0,  1.0,  0.0,
     1.0,  1.0,  0.0,
])

TEXTURED_QUAD_CENTERED = Prefab('TEXTURED_QUAD_CENTERED', [
#      x     y    z    u    v
    -0.5, -0.5, 0.0, 0.0, 1.0,
     0.5, -0.5, 0.0, 1.0, 1.0,
    -0.5,  0.5, 0.0, 0.0, 0.0,
     0.5,  0.5, 0.0, 1.0, 0.0
])

TEXTURED_QUAD = Prefab('TEXTURED_QUAD', [
#     x    y    z    u    v
    0.0, 0.0, 0.0, 0.0, 1.0,
    1.0, 0.0, 0.0, 1.0, 1.0,
    0.0, 1.0, 0.0, 0.0, 0.0,
    1.0, 1.0, 0.0, 1.0, 0.0,
])

def quad(flags='', z=0, box=None, CT=set('ct')):
    flags = set(flags)
    if CT & flags == CT:
        r = TEXTURED_QUAD_CENTERED.data[:]
        w = 5
    elif 't' in flags:
        r = TEXTURED_QUAD.data[:]
        w = 5
    elif 'c' in flags:
        r = QUAD_CENTERED.data[:]
        w = 3
    else:
        w = 3
        return QUAD.data[:]

    # TODO: (hv) flip?

    lr = len(r)
    
    # resize
    if box:
        for c in range(lr//w):
            if r < -EPSILON:
                for i in range(3):
                    r[c*w+i] = box.min[i]
            elif r > -EPSILON:
                for i in range(3):
                    r[c*w+i] = box.max[i]
    
    if z:
        for c in range(lr//w):
            for i in range(3):
                r[c*w+2] = float(z)
    
    return r

# fmt: on

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
