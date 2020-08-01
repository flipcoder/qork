#!/usr/bin/env python
from .node import *
from PIL import Image
import moderngl as gl
from .defs import *
import cson
from glm import ivec2, vec2
from .sprite import *
from .util import *
from .animator import *
from copy import copy
from os import path
import struct


class MeshResource(Resource):
    def __init__(self, app, name, data, shader, meshtype, *args, **kwargs):
        if len(args) == 1:
            assert False
            return
        super().__init__(app, name, *args, **kwargs)
        self.cache = app.cache
        self._data = Reactive(data)
        self.ctx = app.ctx
        self.shader = shader
        self.mesh_type = meshtype
        self.flipped = {}
        self.generated = False
        self.vbo = self.vao = None
        # self.solid = kwargs.pop("solid", False)
        self._box = Lazy(self.calculate_box, [self._data])
        self.on_pend = Signal()

    @property
    def box(self):
        return self._box()

    @property
    def data(self):
        return self._data()

    @data.setter
    def data(self, d):
        self._data(d)
        self.on_pend()

    def __iadd__(self, sig):
        self.on_pend += sig

    def __isub__(self, sig):
        self.on_pend -= sig

    def connect(self, sig, weak=True):
        return self.on_pend.connect(sig, weak)

    def disconnect(self, sig, weak=True):
        return self.on_pend.disconnect(sig, weak)

    def calculate_box(self):
        d = self._data()
        if not d:
            return None
        mini = vec3(float("inf"))
        maxi = -mini
        for i in range(0, len(d), 5):
            for c in range(3):
                idx = i + c
                if d[idx] < mini[c]:
                    mini[c] = d[idx]
                if d[idx] > maxi[c]:
                    maxi[c] = d[idx]

        # check for infs and nans
        for c in (*mini, *maxi):
            if c != c or c == float("inf") or c == float("-inf"):
                print("warning: invalid box for", self)
                self.on_pend()
                return None

        return [mini, maxi]

    def generate(self):
        # if self.generated:
        # if self.vao:
        #     self.vao.delete()
        # if self.vao:
        #     self.vbo.delete()
        # self.vbo = self.ctx.buffer(self.data.astype("f4").tobytes())
        self.vbo = self.ctx.buffer(struct.pack("f" * len(self.data), *self.data))
        # self.vbo = self.ctx.buffer(self.data.bytes())
        self.vao = self.ctx.simple_vertex_array(
            self.shader, self.vbo, "in_vert", "in_text"
        )
        self.generated = True

    def render(self):
        if not self.generated:
            self.generate()
        self.vao.render(self.mesh_type)

    # def __del__(self):
    #     flipped = self.flipped
    #     self.flipped = {}  # prevent recursion
    # if self.generated:
    # if self.vao:
    #     self.vao.delete()
    # if self.vao:
    #     self.vbo.delete()
    # for flip in flipped:
    # flip.cleanup()
    # flip.cleanup = None

    def hflip(self):
        return self.flip("h")

    def vflip(self):
        return self.flip("v")

    def hvflip(self):
        return self.flip("hv")

    def flip(self, flags):
        if ":+" in self.fn:
            assert False  # already flipped, not yet impl
        flags = str(sorted(flags))  # normalize flags
        if flags in self.flipped:
            return self.flipped[flags]
        newdata = self.data.copy()
        for i in range(len(newdata) // 5):
            if "h" in flags:  # flip U coordinate
                newdata[i * 5 + 3] = 1.0 - newdata[i * 5 + 3]
            if "v" in flags:  # flip V cordinate
                newdata[i * 5 + 4] = 1.0 - newdata[i * 5 + 4]
        if self.fn:  # if not temp name, append flags to cached name
            meshname = self.fn + ":+" + flags
        resource = MeshResource(
            self.app,
            meshname,
            newdata,
            self.shader,
            self.mesh_type,
            *self.args,
            **self.kwargs
        )
        # resource.flipped[flags] = self
        flipped = self.flipped[flags] = self.cache.ensure(meshname, resource)
        assert flipped
        return flipped


class Mesh(Node):
    Resource = MeshResource

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.image = kwargs.pop("image", None)
        # for arg in args:
        #     if not isinstance(arg, (str, CoreBase)):
        #         print('image')
        #         self.image = arg

        self.vertices = None
        self.layers = []  # layers -> skins -> images
        self.skin = 0
        self.sprite = None  # frame data here if mesh is a sprite
        self.material = None
        self.frame = 0
        self.loaded = False
        self.resources = []
        self.vbo = None
        self.vao = None
        self.mesh_type = kwargs.get("mesh_type")

        self.data_con = None

        self.filter = kwargs.get("filter")
        self._data = Reactive(kwargs.get("data"))
        # if self._data():
        #     self.connections += self._data().data.connect(self.set_box)

        initfunc = kwargs.get("init")

        if initfunc:
            initfunc(self)

        if self.image or self.fn:
            self.load()

    # resource
    @property
    def data(self):
        return self._data() if self._data else None

    # resource
    @data.setter
    def data(self, d):
        self._data(d)

    def flip(self, flags):
        self.resource = self.resource.hflip(flags)

    def hflip(self):
        self.resource = self.resource.hflip()

    def vflip(self):
        self.resource = self.resource.vflip()

    def hvflip(self):
        self.resource = self.resource.hvflip()

    def load(self, fn=None):
        assert not self.loaded

        fn = self.fn = fn or self.fn  # use either filename from ctor or arg

        # cson = sprite data
        if fn and fn.lower().endswith(".cson"):
            self.sprite = self.app.cache(fn)
            self.resources.append(self.sprite)
            self.layers = self.sprite.layers
            if not self.layers or not self.sprite:
                assert False  # failed to load
            # self.scale(self.sprite['size'])
        else:  # not sprite
            if isinstance(fn, str):
                fns = [fn]
            if not self.image:  # mesh image not preloaded?
                self.layers = self.layers or [[[]]]  # layers -> skins -> images
                for img_fn in fns:
                    # [0][0] = default layer and skin (image list)
                    # p = path.join(self.app.data_path(), img)
                    img = None
                    for dp in self.app._data_paths:
                        try:
                            img = Image.open(path.join(dp, img_fn))
                        except FileNotFoundError:
                            continue
                        break
                    if not img:
                        raise FileNotFoundError()
                    # print(img)
                    img = img.convert("RGBA")
                    self.layers[0][0].append(img)
            else:
                # image preloaded
                if self.image:
                    if not isinstance(self.image, Image):
                        self.image = self.image.data  # unpack image resource
                    self.material = Material(
                        self.ctx.texture(self.image.size, 4, self.image.tobytes())
                    )

        for layer in self.layers:
            for skin in layer:
                for i in range(len(skin)):  # for img in skin:
                    img = skin[i]
                    tex = self.ctx.texture(img.size, 4, img.tobytes())
                    if self.filter:
                        tex.filter = self.filter
                    skin[i] = tex
        # if no data and not temp name
        meshname = ""

        # no prefab or temp name? load a quad for image
        if not isinstance(self.data, Prefab) or (not self.fn or "." not in self.fn):
            self.data = TEXTURED_QUAD_CENTERED
            self.mesh_type = gl.TRIANGLE_STRIP
            self.filter = (gl.NEAREST, gl.NEAREST)
            meshname = self.data.name

        # does cache already have this mesh?
        if self.data:
            if meshname not in self.cache:
                resource = MeshResource(
                    self.app,
                    self.data.name,
                    self.data.data,
                    self.app.shader,
                    self.mesh_type,
                )
                self.resource = self.cache.ensure(meshname, resource)
            else:
                self.resource = self.cache(meshname)
        else:
            self.resource = None

        if self.sprite:
            self.material = Animator(self)
        self.loaded = True

        self.resource_con = self.resource.connect(self.set_local_box)
        self.set_local_box(self.resource.box)

    def update(self, t):
        super().update(t)
        if self.material:
            self.material.update(t)

    def render(self):
        if not self.loaded:
            return
        if self.visible and self.resource:
            self.app.matrix(
                self.world_matrix if self.inherit_transform else self.matrix
            )

            if type(self.material) is Material:  # TEMP
                print('mat')
                self.material.use(i)
            else:
                # TODO: move this to Material/Animator and call material.use(i) above
                for i in range(len(self.layers)):
                    self.layers[i][self.skin][self.frame].use(i)

            self.resource.render()
        super().render()

    # def __del__(self):
    #     super().cleanup()
    #     for r in self.resources:
    #         if r:
    #             r.deref()
