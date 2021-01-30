#!/usr/bin/env python
from .node import *
from PIL import Image
import moderngl as gl
from .prefab import *
from .defs import *
import cson
from glm import ivec2, vec2, vec4
from .sprite import *
from .util import *
from .shaders import Shader
from copy import copy
from os import path
import struct


class MeshResource(Resource):
    def __init__(self, app, *args, **kwargs):
        if len(args) == 1:
            assert False
            return
        super().__init__(*args, **kwargs)

        self.cache = self.app.cache
        self.ctx = self.app.ctx

        self.on_pend = Signal()

        self._data = None

        self.prefab = None
        if isinstance(args[0], Prefab):
            self.prefab = args[0]
            self._data = Reactive(self.prefab.data)
            self.width = self.prefab.width
            self.type = self.prefab.type
        else:
            self._data = Reactive(args[0])
            self.prefab = None
            self.width = kwargs.get("width", 5)
            self.type = kwargs.get("T", gl.TRIANGLES)

        self.shader = args[1]
        assert isinstance(self.shader, Shader)
        # self._type = Reactive(meshtype, [self])
        self.flipped = {}
        self.generated = False
        self.vbo = self.vao = None
        # self.solid = kwargs.pop("solid", False)
        self._box = Lazy(self._calculate_box, [self._data])
        # self.box = self._calculate_box()
        # self._box = Lazy(self._calculate_box, [self._data, self._type])

    @property
    def box(self):
        return self._box()

    @property
    def data(self):
        return self._data()

    @data.setter
    def data(self, d):
        self._data(d)
        # self.on_pend()

    # @property
    # def type(self):
    #     return self.mesh_type

    # @type.setter
    # def type(self, t):
    #     self.mesh_type
    # self.on_pend()

    def __iadd__(self, sig):
        self.on_pend += sig

    def __isub__(self, sig):
        self.on_pend -= sig

    def connect(self, sig, weak=True):
        return self.on_pend.connect(sig, weak)

    def disconnect(self, sig, weak=True):
        return self.on_pend.disconnect(sig, weak)

    def _calculate_box(self):
        d = self.data
        if not d:
            return None
        mini = vec3(float("inf"))
        maxi = -mini
        for i in range(0, len(d), self.width):
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
            self.shader.program, self.vbo, "in_vert", "in_text"
        )
        self.generated = True

    def render(self, material=None):
        if not self.generated:
            self.generate()
        if material:
            material.use()
        self.vao.render(self.type)

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
            # FIXME: this assumes a certain layout
            if "h" in flags:  # flip U coordinate
                newdata[i * 5 + 3] = 1.0 - newdata[i * 5 + 3]
            if "v" in flags:  # flip V cordinate
                newdata[i * 5 + 4] = 1.0 - newdata[i * 5 + 4]
        if self.fn:  # if not temp name, append flags to cached name
            meshname = self.fn + ":+" + flags
        resource = MeshResource(
            self.app,
            Prefab(
                meshname,
                newdata,
            ),
            self.shader,
            # self.type,
            *self.args,
            **self.kwargs
        )
        # resource.flipped[flags] = self
        flipped = self.flipped[flags] = self.cache.ensure(meshname, resource)
        assert flipped
        return flipped


class MeshResourceInstance(ResourceInstance):
    """
    Proxy resource for mesh resource with modified data
    get() gets underlying shared resource, so no need to expose MeshResource methods
    """

    def __init__(self, rc, material=None):
        super().__init__(rc)
        self.material = material

    def update(self, dt):
        mat = self.material
        if mat:
            return mat.update(dt)

    def render(self):
        return self.rc.render(self.material)


class Mesh(Node):
    Resource = MeshResource

    def cube(*args, **kwargs):
        kwargs["prefab"] = Prefab.cube()
        return Mesh(*args, **kwargs)

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
        self.resource_con = Connections()

        self.billboard = False
        self.billboard_matrix = None
        # self.billboard_matrix = Lazy(
        #     self._calculate_billboard_matrix,
        #     [self.app.on_change_camera]
        # )

        self.data_con = None

        self.filter = kwargs.get("filter")
        self._data = Reactive(kwargs.get("data") or kwargs.get("prefab"))
        # self.mesh_type = kwargs.get("mesh_type")
        # if self._data():
        #     self.connections += self._data().data.connect(self.set_box)

        initfunc = kwargs.get("init")

        if initfunc:
            initfunc(self)

        if self.image or self.fn:
            self.load()

    def _calculate_billboard_matrix(self):
        pass

    # resource
    @property
    def data(self):
        return self._data() if self._data else None

    # resource
    @data.setter
    def data(self, d):
        self._data(d)

    def flip(self, flags):
        rcs = self.resources
        for i, rc in enumerate(rcs):
            rcs[i] = rc.hflip(flags)

    def hflip(self):
        rcs = self.resources
        for i, rc in enumerate(rcs):
            rcs[i] = rc.hflip()

    def vflip(self):
        rcs = self.resources
        for i, rc in enumerate(rcs):
            rcs[i] = rc.vflip()

    def hvflip(self):
        rcs = self.resources
        for i, rc in enumerate(rcs):
            rcs[i] = rc.hvflip()

    # TODO: This function is ugly.  Improve it!
    def load(self, fn=None):
        assert not self.loaded

        fn = self.fn = fn or self.fn  # use either filename from ctor or arg

        # cson = sprite data
        if fn and fn.lower().endswith(".cson"):
            self.sprite = self.app.cache(fn)
            assert isinstance(self.sprite, Sprite)
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
                    self.image = img = img.convert("RGBA")
                    self.layers[0][0].append(self.image)
                    self.material = Material(
                        self.ctx.texture(img.size, 4, img.tobytes())
                    )
            else:
                # image preloaded
                if self.image:
                    # if not isinstance(self.image, Image.Image):
                    #     data = self.image.data  # unpack image resource
                    self.image = self.image.convert("RGBA")
                    self.material = Material(
                        self.ctx.texture(self.image.size, 4, self.image.tobytes())
                    )

        for layer in self.layers:
            for skin in layer:
                for i in range(len(skin)):  # for img in skin:
                    img = skin[i]
                    tex = self.ctx.texture(img.size, 4, img.tobytes())
                    tex.filter = (gl.NEAREST, gl.NEAREST)
                    tex.repeat_x = False
                    tex.repeat_y = False
                    if self.filter:
                        tex.filter = self.filter
                    skin[i] = tex
        # if no data and not temp name
        meshname = ""

        # no prefab or temp name? load a quad for image
        if not self.data or (not self.fn or "." not in self.fn):
            self.data = TEXTURED_QUAD_CENTERED
            # self.type = self.data.type
            if not self.filter:
                self.filter = (gl.NEAREST, gl.NEAREST)
            meshname = self.data.name  # for caching

        # does cache already have this mesh?
        if self.data:
            if meshname not in self.cache:
                resource = MeshResource(
                    self.app,
                    # self.data.name,
                    # self.data.data,
                    self.data,
                    self.app.shader,
                    # self.data.type,
                )
                self.resources = [self.cache.ensure(meshname, resource)]
            else:
                self.resources = [self.cache(meshname)]
        else:
            self.resources = []

        if self.sprite:
            self.material = SpriteMaterial(self.sprite)
            self.material += self.on_state_change.connect(
                lambda category, value: self.material.state(category, value)
            )

        self.loaded = True

        for rc in self.resources:
            self.resource_con += rc.connect(self.set_local_box)

            # TODO: combine resoure boxes
            self.set_local_box(rc.box)

    def update(self, dt):
        super().update(dt)

        if self.material:
            self.material.update(dt)

        for rc in self.resources:
            rc.update(dt)

    def render(self):
        if not self.loaded:
            return
        if self.visible and self.resources:
            if self.billboard:
                self.app.matrix(self.billboard_matrix)
            else:
                self.app.matrix(
                    self.world_matrix  # if self.inherit_transform else self.matrix
                )

            if self.material:
                self.material.use()

            for rc in self.resources:
                rc.render()

        super().render()

    def calculate_vertices(self, recursive=False):
        rc = self.resource
        data = rc.data
        sz = len(data) // rc.width
        r = [None] * sz
        for i in range(sz):
            j = i * rc.width
            vert = vec3(*data[j : j + 3])
            uv = vec2(*data[j + 3 : j + 5])
            vert = (self.world_matrix * vec4(vert, 1.0)).xyz
            r[i] = [*vert, *uv]
        if recursive:
            for ch in self.children:
                r += ch.calculate_vertices(recursive=recursive)
        return r

    # def __del__(self):
    #     super().cleanup()
    #     for r in self.resources:
    #         if r:
    #             r.deref()
