#!/usr/bin/env python

import cairo
import math

from .node import *

import moderngl as gl
from moderngl_window import geometry

from glm import vec2, ivec2
from qork import easy

# @mixin(cairo.Context, 'ctx')
class Canvas(Node, cairo.Context):
    def __new__(self, cls, *args, **kwargs):
        r = super(cairo.Context, cls).__new__(cls)
        r.__init__(*args, **kwargs)
        return r

    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)

        # self.size = to_vec3(kwargs.get('size'))

        self.quad_fs = geometry.quad_fs()

        self.dirty = True

        isz = ivec2(1024, 1024)

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *isz)

        # cairo.Context.__init__(self, self.surface)
        self.ctx = cairo.Context(self.surface)

        self.shader = self.app.ctx.program(
            vertex_shader="""
                #version 330
                in vec3 in_position;
                in vec2 in_texcoord_0;
                out vec2 uv;
                void main() {
                    gl_Position = vec4(in_position, 1.0);
                    uv = in_texcoord_0;
                }
            """,
            fragment_shader="""
                #version 330
                uniform sampler2D texture0;
                in vec2 uv;
                out vec4 outColor;
                void main() {
                    outColor = texture(texture0, uv);
                }
            """,
        )

        self.on_render = Signal()
        # self.connections += self.on_resize.connect(lambda: self.set_dirty(True))

        self.texture = None

    def set_dirty(self, b=True):
        self.dirty = b

    def render(self):
        if not self.texture:
            return

        if self.dirty:
            self.on_render()
            self.texture = self.app.ctx.texture(isz, 4, data=self.surface.get_data())
            self.dirty = False

        self.app.ctx.enable(gl.BLEND)
        self.texture.use(location=0)
        self.quad_fs.render(self.shader)
