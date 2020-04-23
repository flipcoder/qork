#!/usr/bin/env python

import cairo
import math
import copy

from .node import *

import moderngl as gl
from moderngl_window import geometry

from glm import vec2, ivec2
from qork import easy

# @mixin(cairo.Context, 'ctx')
class Canvas(Node):
    # def __new__(cls, *args, **kwargs):
    #     surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *isz)
    #     ctx = cairo.Context(self.surface)
    #     cairo.Context.__new__(cls, ctx)
    #     return cls.__init__(self, ctx, surface, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)

        # self.size = to_vec3(kwargs.get('size'))

        self.quad_fs = geometry.quad_fs()

        self.dirty = True

        isz = ivec2(1024, 1024)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *isz)
        self.cairo_ctx = cairo.Context(self.surface)

        # cairo.Context.__init__(self, self.surface)

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

# Mix in cairo context members

reserved_names = ['translate']

for name, method in cairo.Context.__dict__.items():
    if name.startswith('_'):
        continue
    
    try:
        getattr(Canvas, name) 
        name = 'canvas_' + name # resolve name conflicts
        getattr(Canvas, name)
        assert False
    except AttributeError:
        pass
    
    if name in reserved_names:
        name = 'canvas_' + name
    
    def f(self, *args, **kwargs):
        r = method(self.ctx, *args, **kwargs)
        self.dirty = True
        return r
    # f.__name__ = name
    setattr(Canvas, name, f)
    # print(name, f)

