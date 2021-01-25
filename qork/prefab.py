#!/usr/bin/env python

import moderngl as gl
from qork.util import *


class Prefab:
    def __init__(self, *args):
        self.name = try_get(args, 0)
        self.data = try_get(args, 1)
        self.type = try_get(args, 2, gl.TRIANGLES)
        self.layout = try_get(args, 3, "xyz")
        self.width = len(self.layout)


# fmt: off
QUAD_TS = Prefab('QUAD_TS', [
#     x    y    z
   0.0, 0.0, 0.0,
   1.0, 0.0, 0.0,
   0.0, 1.0, 0.0,
   1.0, 1.0, 0.0,
], gl.TRIANGLE_STRIP, 'xyz')

QUAD = Prefab('QUAD', [
#     x    y    z
   0.0, 0.0, 0.0,
   1.0, 0.0, 0.0,
   0.0, 1.0, 0.0,
   0.0, 1.0, 0.0,
   1.0, 1.0, 0.0,
   1.0, 0.0, 0.0,
], gl.TRIANGLES, 'xyz')

QUAD_CENTERED = Prefab('QUAD_CENTERED', [
#      x     y    z    u    v
    -0.5, -0.5, 0.0,
     0.5, -0.5, 0.0,
    -0.5,  0.5, 0.0,
    -0.5,  0.5, 0.0,
     0.5, -0.5, 0.0,
     0.5,  0.5, 0.0,
], gl.TRIANGLES, 'xyz')

QUAD_CENTERED_TS = Prefab('QUAD_CENTERED_TS', [
#      x    y    z
    -0.5, -0.5,  0.0,
     0.5, -0.5,  0.0,
    -0.5,  0.5,  0.0,
     0.5,  0.5,  0.0,
], gl.TRIANGLE_STRIP, 'xyz')

TEXTURED_QUAD_CENTERED_TS = Prefab('TEXTURED_QUAD_CENTERED_TS', [
#      x     y    z    u    v
    -0.5, -0.5, 0.0, 0.0, 1.0,
     0.5, -0.5, 0.0, 1.0, 1.0,
    -0.5,  0.5, 0.0, 0.0, 0.0,
     0.5,  0.5, 0.0, 1.0, 0.0,
], gl.TRIANGLE_STRIP, 'xyzuv')

TEXTURED_QUAD_CENTERED = Prefab('TEXTURED_QUAD_CENTERED', [
#      x     y    z    u    v
    -0.5, -0.5, 0.0, 0.0, 1.0,
     0.5, -0.5, 0.0, 1.0, 1.0,
    -0.5,  0.5, 0.0, 0.0, 0.0,
    -0.5,  0.5, 0.0, 0.0, 0.0,
     0.5, -0.5, 0.0, 1.0, 1.0,
     0.5,  0.5, 0.0, 1.0, 0.0,
], gl.TRIANGLES, 'xyzuv')

TEXTURED_QUAD_TS = Prefab('TEXTURED_QUAD_TS', [
#     x    y    z    u    v
   0.0, 0.0, 0.0, 0.0, 1.0,
   1.0, 0.0, 0.0, 1.0, 1.0,
   0.0, 1.0, 0.0, 0.0, 0.0,
   1.0, 1.0, 0.0, 1.0, 0.0,
], gl.TRIANGLE_STRIP, 'xyzuv')

TEXTURED_CUBE_CENTERED = Prefab('TEXTURED_CUBE', [
    -0.5, -0.5, 0.5, 0.0, 1.0, 
    0.5, -0.5, 0.5, 1.0, 1.0, 
    -0.5, 0.5, 0.5, 0.0, 0.0, 
    -0.5, 0.5, 0.5, 0.0, 0.0, 
    0.5, -0.5, 0.5, 1.0, 1.0, 
    0.5, 0.5, 0.5, 1.0, 0.0, 
    0.5, -0.5, -0.5, 0.0, 1.0, 
    -0.5, -0.5, -0.5, 1.0, 1.0, 
    0.5, 0.5, -0.5, 0.0, 0.0, 
    0.5, 0.5, -0.5, 0.0, 0.0, 
    -0.5, -0.5, -0.5, 1.0, 1.0, 
    -0.5, 0.5, -0.5, 1.0, 0.0, 
    -0.5, -0.5, -0.5, 0.0, 1.0, 
    -0.5, -0.5, 0.5, 1.0, 1.0, 
    -0.5, 0.5, -0.5, 0.0, 0.0, 
    -0.5, 0.5, -0.5, 0.0, 0.0, 
    -0.5, -0.5, 0.5, 1.0, 1.0, 
    -0.5, 0.5, 0.5, 1.0, 0.0, 
    0.5, -0.5, 0.5, 0.0, 1.0, 
    0.5, -0.5, -0.5, 1.0, 1.0, 
    0.5, 0.5, 0.5, 0.0, 0.0, 
    0.5, 0.5, 0.5, 0.0, 0.0, 
    0.5, -0.5, -0.5, 1.0, 1.0, 
    0.5, 0.5, -0.5, 1.0, 0.0, 
    -0.5, 0.5, 0.5, 0.0, 1.0, 
    0.5, 0.5, 0.5, 1.0, 1.0, 
    -0.5, 0.5, -0.5, 0.0, 0.0, 
    -0.5, 0.5, -0.5, 0.0, 0.0, 
    0.5, 0.5, 0.5, 1.0, 1.0, 
    0.5, 0.5, -0.5, 1.0, 0.0, 
    -0.5, -0.5, -0.5, 0.0, 1.0, 
    0.5, -0.5, -0.5, 1.0, 1.0, 
    -0.5, -0.5, 0.5, 0.0, 0.0, 
    -0.5, -0.5, 0.5, 0.0, 0.0, 
    0.5, -0.5, -0.5, 1.0, 1.0, 
    0.5, -0.5, 0.5, 1.0, 0.0, 
], gl.TRIANGLES, 'xyzuv')

# fmt: on


def prefab_quad(flags="", z=0, box=None, CT=set("ct")):
    flags = set(flags)
    if CT & flags == CT:
        r = TEXTURED_QUAD_CENTERED.data[:]
        w = 5
    elif "t" in flags:
        r = TEXTURED_QUAD.data[:]
        w = 5
    elif "c" in flags:
        r = QUAD_CENTERED.data[:]
        w = 3
    else:
        w = 3
        return QUAD.data[:]

    # TODO: (hv) flip?

    lr = len(r)

    # resize
    if box:
        for c in range(lr // w):
            if r < -EPSILON:
                for i in range(3):
                    r[c * w + i] = box.min[i]
            elif r > -EPSILON:
                for i in range(3):
                    r[c * w + i] = box.max[i]

    if z:
        for c in range(lr // w):
            for i in range(3):
                r[c * w + 2] = float(z)

    return r


Prefab.quad = prefab_quad


def prefab_cube(flags="", box=None, DEF=set("ct")):
    # TODO
    flags = set(flags)
    return TEXTURED_CUBE_CENTERED


Prefab.cube = prefab_cube
