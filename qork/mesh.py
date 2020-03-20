#!/usr/bin/env python
from .node import *
import numpy as np
from PIL import Image
import moderngl as gl
from .defs import *
import cson
from glm import ivec2, vec2
from .sprite import *
from .util import *
from .animator import *
from copy import copy

class MeshBuffer(Resource):
    def __init__(
        self, name, data, cache, ctx, shader, meshtype, *args, **kwargs
    ):
        if len(args) == 1:
            return
        super().__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.name = name
        self.cache = cache
        self.data = data
        self.ctx = ctx
        self.shader = shader
        self.mesh_type = meshtype
        self.flipped = {}
        self.generated = False
        self.vbo = self.vao = None
    def generate(self):
        if self.generated:
            if self.vao:
                self.vao.delete()
            if self.vao:
                self.vbo.delete()
        self.vbo = self.ctx.buffer(self.data.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(
            self.shader, self.vbo, 'in_vert', 'in_text'
        )
        self.generated = True
    def render(self):
        if not self.generated:
            self.generate()
        self.vao.render(self.mesh_type)
    def cleanup(self):
        flipped = self.flipped
        self.flipped = {} # prevent recursion
        if self.generated:
            if self.vao:
                self.vao.delete()
            if self.vao:
                self.vbo.delete()
        for flip in flipped:
            flip.cleanup()
            flip.cleanup = None
    def hflip(self):
        return self.flip('h')
    def vflip(self):
        return self.flip('v')
    def hvflip(self):
        return self.flip('hv')
    def flip(self, flags):
        if ':+' in self.name:
            assert False # already flipped, not yet impl
        flags = str(sorted(flags)) # normalize flags
        if flags in self.flipped:
            return self.flipped[flags]
        newdata = self.data.copy()
        for i in range(len(newdata) // 5):
            if 'h' in flags: # flip U coordinate
                newdata[i * 5 + 3] = 1.0 - newdata[i * 5 + 3]
            if 'v' in flags: # flip V cordinate
                newdata[i * 5 + 4] = 1.0 - newdata[i * 5 + 4]
        meshname = self.name + ':+' + flags
        meshdata = MeshBuffer(
            meshname,
            newdata,
            self.cache,
            self.ctx,
            self.shader,
            self.mesh_type,
            *self.args,
            **self.kwargs
        )
        # meshdata.flipped[flags] = self
        flipped = self.flipped[flags] = self.cache.ensure(
            meshname,
            meshdata
        )
        assert flipped
        return flipped

class Mesh(Node):
    def __init__(self, app=None, fn=None, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.vertices = None
        self.layers = [] # layers -> skins -> images
        self.fn = fn
        self.skin = 0
        self.sprite = None # frame data here if mesh is a sprite
        self.animator = None
        self.image = None
        self.frame = 0
        self.loaded = False
        self.resources = []
        self.vbo = None
        self.vao = None
        self.mesh_type = kwargs.get('mesh_type')
        
        pos = kwargs.get('position') or kwargs.get('pos')
        scale = kwargs.get('scale')
        self.filter = kwargs.get('filter')
        self.data = kwargs.get('data')
        scale = kwargs.get('scale')
        rot = kwargs.get('rot') or kwargs.get('rotation')
        initfunc = kwargs.get('init')
        
        if pos is not None:
            self.position(pos)
        if scale is not None:
            self.scale(scale)
        if rot is not None:
            self.rotate(*rot)
        
        if initfunc:
            initfunc(self)
        
        if self.fn:
            load()
    def flip(self, flags):
        self.meshdata = self.meshdata.hflip(flags)
    def hflip(self):
        self.meshdata = self.meshdata.hflip()
    def vflip(self):
        self.meshdata = self.meshdata.vflip()
    def hvflip(self):
        self.meshdata = self.meshdata.hvflip()
    def load(self, fn=None):
        if self.loaded:
            return
        
        fn = self.fn = fn or self.fn # use either filename from ctor or arg

        # cson = sprite data
        if fn and fn.lower().endswith('.cson'):
            self.sprite = self.app.cache(fn)
            self.resources.append(self.sprite)
            self.layers = self.sprite.layers
            if not self.layers or not self.sprite:
                assert False # failed to load
            # self.scale(self.sprite['size'])
        else: # not sprite
            if isinstance(fn, str):
                fn = [fn]
            if not self.image: # mesh image not preloaded?
                self.layers = self.layers or [[[]]] # layers -> skins -> images
                for img in fn:
                    # [0][0] = default layer and skin (image list)
                    self.layers[0][0].append(Image.open(img).convert('RGBA'))
        for layer in self.layers:
            for skin in layer:
                for i in range(len(skin)): # for img in skin:
                    img = skin[i]
                    tex = self.ctx.texture(img.size, 4, img.tobytes())
                    if self.filter:
                        tex.filter = self.filter
                    skin[i] = tex
        # data provided in tuple as seen in defs.py
        if type(self.data) == tuple:
            meshname = self.data[0]
            # does cache already have this mesh?
            if not self.cache.has(meshname):
                meshdata = MeshBuffer(
                    *self.data, # expand name and buffer
                    self.cache,
                    self.ctx,
                    self.app.shader,
                    self.mesh_type
                )
                self.meshdata = self.cache.ensure(meshname, meshdata)
            else:
                self.meshdata = self.cache(meshname)
        if self.sprite:
            self.animator = Animator(self)
        self.loaded = True
    def logic(self, t):
        super().logic(t)
        if self.animator:
            self.animator.logic(t)
    def render(self):
        if self.visible and self.meshdata:
            self.app.matrix(self.matrix(WORLD))
            for i in range(len(self.layers)):
                self.layers[i][self.skin][self.frame].use(i)
            self.meshdata.render()
        super().render()
    def cleanup(self):
        for r in self.resources:
            if r:
                r.deref()
        self.resources = []
        super().cleanup()

