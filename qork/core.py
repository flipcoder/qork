#!/usr/bin/env python
import glm
import moderngl as gl
import moderngl_window as mglw
from .defs import *
from .cache import *
from .sprite import *
from .util import *
import cson
import os

class Core(mglw.WindowConfig):
    gl_version = (3, 3)
    window_size = (960, 540)
    aspect_ratio = 16 / 9
    resizable = True
    samples = 4
    resource_dir = os.path.normpath(os.path.join(__file__, '../../data/'))
    
    @classmethod
    def run(cls):
        mglw.run_window_config(cls)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cleanup_list = [] # nodes awaiting dtor/destuctor/deinit calls
        self.camera = None
        self.bg_color = (0,0,0)
        self.cache = Cache(self.resolve_resource)
        self.cache.register_transformer(self.transform_resource)
    def logic(self, dt):
        self.root.logic(dt)
        self.clean()
    def clean(self):
        if self.cleanup_list:
            for entity in self.cleanup_list:
                entity.cleanup()
            self.cleanup_list = []
    def transform_resource(self, Class, *args, **kwargs):
        args = ([self] + list(args))
        return Class, args, kwargs
    def resolve_resource(self, *args, **kwargs):
        fn = filename(*args, **kwargs)
        assert fn
        fnl = fn.lower()
        for ext in ['.cson']:
            with open(fn, 'rb') as f:
                data = cson.load(f)
                if data['type']=='sprite':
                    return Sprite
        for ext in ['.png','.jpg']:
            if fnl.endswith(ext):
                return Image
    def render(self, time, dt):
        self.dt = dt
        self.time = time
        self.logic(dt)
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(gl.DEPTH_TEST | gl.CULL_FACE)
        if self.camera:
            self.shader['Projection'] = flatten(self.camera.projection)
            self.shader['View'] = flatten(glm.inverse(self.camera.matrix(WORLD)))
        self.root.render()

