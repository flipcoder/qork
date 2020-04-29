#!/usr/bin/env python

import cairo
import math
import copy
import webcolors

from .mesh import *
from .shaders import *
from .util import *
from collections import deque

import moderngl as gl
from moderngl_window import geometry

from glm import vec2, ivec2
from qork import easy

# @mixin(cairo.Context, 'ctx')
class Canvas(Mesh):
    # def __new__(cls, *args, **kwargs):
    #     surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *isz)
    #     ctx = cairo.Context(self.surface)
    #     cairo.Context.__new__(cls, ctx)
    #     return cls.__init__(self, ctx, surface, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        args, kwargs = remove_filename(args, kwargs)
        super().__init__(*args, **kwargs)

        # self.size = to_vec3(kwargs.get('size'))

        # self.quad_fs = geometry.quad_fs()

        self.resource = MeshResource(self.app, '', TEXTURED_QUAD_CENTERED.data, self.app.shader, gl.TRIANGLE_STRIP)
        # self.resource_con = self.resource.connect(self.set_local_box)
        self.set_local_box(self.resource.box)
        self._source = None
        
        self.loaded = True
        self.stack: deque[Connections] = deque() # Connections stack
        
        res = kwargs.pop('res', self.app.size)
        self.res = ivec2(*res)
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.res)
        self.cairo = cairo.Context(self.surface)

        # cairo.Context.__init__(self, self.surface)

        # self.shader = self.app.ctx.shader(SHADER_BASIC)

        # self.shader = self.app.ctx.program(
        #     vertex_shader="""
        #         #version 330
        #         in vec3 in_position;
        #         in vec2 in_texcoord_0;
        #         out vec2 uv;
        #         void main() {
        #             gl_Position = vec4(in_position, 1.0);
        #             uv = in_texcoord_0;
        #         }
        #     """,
        #     fragment_shader="""
        #         #version 330
        #         uniform sampler2D texture0;
        #         in vec2 uv;
        #         out vec4 outColor;
        #         void main() {
        #             outColor = texture(texture0, uv).zyxw; // BGRA -> RGBA
        #         }
        #     """,
        # )

        self.on_render = Signal()
        # self.connections += self.on_resize.connect(lambda: self.set_dirty(True))

        self.texture = None
        self.dirty = True
        self._use_text = False

        self.clear()
        text = kwargs.pop('text', None)
        if text is not None:
            self.text(text)

        # self.shadow = False

    def refresh(self):
        self.dirty = True

    @property
    def w(self):
        return self.res[0]

    @property
    def h(self):
        return self.res[1]

    @property
    def source(self):
        return self._source
        
    @source.setter
    def source(self, col):
        print('source', col)
        col = color(col)
        self.on_render += lambda col=col: self.set_source_rgba(*col)
        self._source = col
        self.dirty = True

    def font(self, *args):
        name = ''
        sz = None
        if args:
            for a in args:
                ta = type(a)
                if ta in (int, float):
                    sz = a
                elif ta is str:
                    name = a
        if sz is None:
            sz = self.app.size[0] // 15
        print(sz)
        def f():
            self.cairo.set_font_face(cairo.ToyFontFace(name))
            self.cairo.set_font_size(sz)
        self.on_render += f
        self._use_text = True
        self.dirty = True

    def text(self, s, pos=(0,0), col=None, align=''):
        if not self._use_text:
            self.font()
            self._use_text = True
        def f(s=s, pos=pos, align=align):
            if col is not None:
                self.cairo.set_source_rgba(*color(col))
            
            extents = self.cairo.text_extents(s)
            
            print(extents)
            # x = extents[2]//2 if 'h' in align else 0
            # y = -extents[3]//2 if 'v' in align else 0
            x = -extents[2]//2
            y = extents[3]//4

            self.cairo.move_to(int(pos[0]) + x, int(pos[1]) + y)
            self.cairo.show_text(s)
        self.on_render += f
        self.dirty = True

    def clear(self):
        self.on_render.clear()
        def f():
            # self.cairo.set_operator(cairo.OPERATOR_CLEAR)
            # self.cairo.paint()
            self.cairo.rectangle(0, 0, *self.res)
            self.cairo.set_source_rgba(0,0,0,0)
            self.cairo.fill()
        self.on_render += f
        self.dirty = True
    
    def push(self):
        c = Connections()
        self.stack.append(c)
        return c

    def pop(self, c=None):
        if c is None:
            c = self.stack.pop()
        else:
            self.stack.remove(c)
        return c
    
    def render(self):
        
        if not self.visible:
            return
        
        if self.dirty:
            self.on_render()
            data = self.surface.get_data()
            # for i in range(len(data)//4): # ABGR -> RGBA
            #     data[i+3] = data[i]
            #     data[i+1] = data[i+2]
            # print(list(data[0:4]))
            # img = Image.frombuffer("ABGR",tuple(self.res),data,"raw","RGBA",0,1)
            # img.show()
            self.texture = self.app.ctx.texture(self.res, 4, data=data)
            self.dirty = False
        
            # img.show()
        
        self.app.matrix(
            self.world_matrix if self.inherit_transform else self.matrix
        )
        
        self.texture.use()
        self.resource.render()

        Node.render(self)

        # if self.texture:
        #     self.app.ctx.enable(gl.BLEND)
        #     self.texture.use(location=0)
            # self.quad_fs.render(self.shader)


# Mix in cairo context members

reserved_names = ["translate"]

for name, method in cairo.Context.__dict__.items():
    if name.startswith("_"):
        continue

    try:
        getattr(Canvas, name)
        name = "canvas_" + name  # resolve name conflicts
        getattr(Canvas, name)
        assert False
    except AttributeError:
        pass

    if name in reserved_names:
        name = "canvas_" + name

    def f(self, *args, name=name, method=method, **kwargs):
        print(name, args, kwargs)
        slot = self.on_render.connect(lambda method=method: method(self.cairo, *args, **kwargs), weak=False)
        if self.stack:
            self.stack[-1] += slot
        self.dirty = True
        return slot
        # return method(self.cairo, *args, **kwargs)
        # return slot

    # f.__name__ = name
    setattr(Canvas, name, f)
    # print(name, f)
