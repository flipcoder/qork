#!/usr/bin/env python

import cairo
import math
import copy
import webcolors
import array
import numpy as np

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

        self.resource = self.cache(
            TEXTURED_QUAD_CENTERED.name,
            lambda: MeshResource(
                self.app,
                TEXTURED_QUAD_CENTERED,
                # TEXTURED_QUAD_CENTERED.name,
                # TEXTURED_QUAD_CENTERED.data,
                self.app.shader,
                # TEXTURED_QUAD_CENTERED.type,
            ),
        )
        # self.resource_con = self.resource.connect(self.set_local_box)
        self.set_local_box(self.resource.box)
        self._source = None

        self.loaded = True
        self.stack: deque[Connections] = deque()  # Connections stack

        res = kwargs.pop("res", ivec2(1024, 1024))
        self.res = ivec2(res)
        self.buf = np.zeros(self.res[0] * self.res[1] * 4, dtype=np.int8)
        self.buf.reshape(4, self.res[0], self.res[1])

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.res)
        self.cairo = cairo.Context(self.surface)

        self.on_render = Signal()
        self.refresh()
        # self.connections += self.on_resize.connect(lambda: self.set_dirty(True))

        self.texture = None
        self._use_text = False

        self.clear(kwargs.get("color"))
        text = kwargs.pop("text", None)
        if text:
            self.text(text)

        grad = kwargs.pop("gradient", None) or kwargs.pop("grad", None)
        if grad:
            self.gradient(grad)
        # self.shadow = False

    def gradient(self, *colors, region=None):
        if not colors:
            return None

        # TODO: check colors for Gradient object, use that instead
        # TODO: allow reactive colors (Rcolor)

        if region is None:
            # grad = cairo.LinearGradient(0, 0, *self.res)
            grad = cairo.LinearGradient(0, 0, 0, self.res[1])
        else:
            grad = cairo.LinearGradient(*region)

        # is there stops? or just one color
        # stops = type(colors[0]) in (tuple, list)

        # # allow color or (step, color)
        # if type(colors[0]) in (tuple, list):
        #     interps = list(map(lambda s: s[0], colors))
        #     colors = list(map(lambda s: s[1], colors))
        # else:
        #     interps = None

        stops = len(colors)
        # for i, col in enumerate(colors):
        #     if type(col) in (tuple,list): # unpack (stop, color)
        #         stops += 1

        for i, col in enumerate(colors):
            if type(col) in (tuple, list):  # unpack (stop, color)
                stop = colors[i][0]
                col = col[1]
                # print(stop, col)
            else:
                stop = i / max(1, stops - 1)  # auto
            col = Color(col).rgb
            # print(col)
            # print(stop)
            grad.add_color_stop_rgb(stop, *col)

        def f():
            self.cairo.rectangle(0, 0, *self.res)
            self.cairo.set_source(grad)
            self.cairo.fill()

        self.on_render += f
        self.refresh()
        return grad

    # def refresh(self):
    #     self.dirty = True

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
        # print('source', col)
        self._source = col = Color(col)
        self.on_render += lambda col=col: self.set_source_rgba(*col)
        self.refresh()

    def font(self, *args):
        name = ""
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
        # print(sz)
        def f():
            self.cairo.set_font_face(cairo.ToyFontFace(name))
            self.cairo.set_font_size(sz)

        self.on_render += f
        self.refresh()
        self._use_text = True

    def text(self, s, col="white", pos=None, flags="c", shadow=None):
        """
        :param align: string: char flags
            l: relative to left
            r: relative to right
            t: relative to top
            b: relative to bottom
        """
        full_args = locals()

        if not self._use_text:
            self.font()
            self._use_text = True

        col = Color(col)

        if pos is None:
            pos = vec2(0)
        else:
            pos = copy(pos)

        if flags:
            for ch in flags:
                if ch == "l":
                    pos += ivec2(-self.res[0] // 2, 0)
                elif ch == "r":
                    pos += ivec2(self.res[0] // 2, 0)
                elif ch == "t":
                    pos += ivec2(0, -self.res[1] // 2)
                elif ch == "b":
                    pos += ivec2(0, self.res[1] // 2)

        if shadow is True:  # True, but not a vector
            shadow = vec2(-3, 3)

        def f(s=s, pos=pos):

            # this has to be called in f, since the order of this func matters
            extents = self.cairo.text_extents(s)

            # print(extents)
            origin = self.res / 2
            # pos -= ivec2(extents.width, extents.height)/2
            pos.x -= extents.width / 2
            pos.y += extents.height / 4
            # pos.y -= extents.height // 2
            if "c" in flags or "h" in flags:
                pos.x += origin.x
            if "c" in flags or "v" in flags:
                pos.y += origin.y
            # pos offsets
            # print(pos)
            # print(x, y)

            if shadow:
                self.cairo.set_source_rgba(0, 0, 0, 1)
                self.cairo.move_to(*(pos + shadow))
                self.cairo.show_text(s)

            self.cairo.set_source_rgba(*col)
            self.cairo.move_to(*pos)
            self.cairo.show_text(s)

        self.on_render += f
        # self.on_render.store(f, name='text(' + str(full_args) + ')')
        self.refresh()

    def clear(self, col=None):
        if col is not None:
            col = Color(col)

        self.on_render.clear()
        self.stack.clear()

        def f():
            # self.cairo.rectangle(0, 0, *self.res)
            # self.cairo.set_source_rgba(*col)
            if col is None:
                self.cairo.set_source_rgba(0, 0, 0, 0)
                self.cairo.set_operator(cairo.OPERATOR_CLEAR)
                self.cairo.paint()
                self.cairo.set_operator(cairo.OPERATOR_OVER)
            else:
                self.cairo.set_source_rgba(*col)
                self.cairo.paint()

        # self.on_render += f
        self.on_render.store(f, name="clear")
        self.refresh()

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

    def refresh(self, b=True, /, now=False, preview=False):
        """
        (default): sets dirty flag to b value
        b: dirty flag state
        now: redraws if refresh needed
        preview: show image preview
        """

        if not now:
            self.dirty = b
            return

        assert b == True  # b==False and now==True ?

        if self.dirty:

            self.on_render()

            buf = self.surface.get_data()

            if self.texture:
                self.texture.release()
            self.texture = self.app.ctx.texture(self.res, 4, buf)
            self.texture.swizzle = "BGRA"

            self.dirty = False

            # img.show()

    def preview(self):
        self.refresh(now=True)
        data = self.surface.get_data()
        # img = Image.frombuffer("RGBA", tuple(self.res), data, "raw", "RGBA", 0, 1)
        img.show()

    def render(self):

        if not self.visible:
            return

        self.refresh(now=True)

        self.app.matrix(self.world_matrix if self.inherit_transform else self.matrix)

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
        # print(name, args, kwargs)
        slot = self.on_render.connect(
            lambda method=method: method(self.cairo, *args, **kwargs), weak=False
        )
        if self.stack:
            self.stack[-1] += slot
        self.dirty = True
        return slot
        # return method(self.cairo, *args, **kwargs)
        # return slot

    # f.__name__ = name
    setattr(Canvas, name, f)
    # print(name, f)
