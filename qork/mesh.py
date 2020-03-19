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
from copy import copy

class MeshBuffer(Resource):
    def __init__(self, name, data, ctx, shader, meshtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.data = data.copy()
        self.ctx = ctx
        self.shader = shader
        self.mesh_type = meshtype
        self.vbo = self.ctx.buffer(self.data.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.shader, self.vbo, 'in_vert', 'in_text')
    def render(self):
        self.vao.render(self.mesh_type)

class Mesh(Node):
    def __init__(self, app, fn=None, **kwargs):
        super().__init__(app, **kwargs)
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
        data = kwargs.get('data')
        scale = kwargs.get('scale')
        rot = kwargs.get('rot') or kwargs.get('rotation')
        initfunc = kwargs.get('init')
        
        if data:
            self.data = data
        if pos != None:
            self.position(pos)
        if scale != None:
            self.scale(scale)
        if rot != None:
            self.rotate(*rot)
        
        if initfunc:
            initfunc(self)
        
        if self.fn:
            load()
    def load(self, fn=None):
        if self.loaded: return
        
        fn = self.fn = fn or self.fn # use either filename from ctor or arg

        # json = sprite data
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
                    # print(img.size)
                    skin[i] = self.ctx.texture(img.size, 4, img.tobytes())
        if type(self.data) == tuple:
            meshdata = MeshBuffer(
                *self.data, # name and buffer
                self.ctx,
                self.app.shader,
                self.mesh_type
            )
            self.meshdata = self.app.cache.ensure(
                meshdata.name,
                meshdata
            )
        self.loaded = True
    def logic(self, t):
        super().logic(t)
        if self.animator:
            self.animator.logic(t)
    def render(self):
        if self.visible:
            self.app.shader['Model'] = flatten(self.matrix(WORLD))
            for i in range(len(self.layers)):
                self.layers[i][self.skin][self.frame].use(i)
            self.meshdata.render()
        super().render()
    def cleanup(self):
        for r in self.resources:
            if r:
                r.cleanup()

