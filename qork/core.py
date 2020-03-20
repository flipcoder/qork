#!/usr/bin/env python
import glm
import sys
if __debug__:
    sys.argv += ['--vsync','off']
import moderngl as gl
import moderngl_window as mglw
from .defs import *
from .cache import *
from .sprite import *
from .util import *
from .reactive import *
import cson
import os

# class RenderPass
#     def __init__(self, camera):
#         self.camera = camera

class Core(mglw.WindowConfig):
    gl_version = (3, 3)
    window_size = (960, 540)
    aspect_ratio = 16 / 9
    resizable = True
    samples = 4
    title = 'qork'
    resource_dir = os.path.normpath(os.path.join(__file__, '../../data/'))
    
    @classmethod
    def run(cls):
        mglw.run_window_config(cls)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_resize = Signal()
        self.cleanup_list = [] # nodes awaiting dtor/destuctor/deinit calls
        self.camera = None
        self.bg_color = (0,0,0)
        self.cache = Cache(self.resolve_resource, self.transform_resource)
        # self.renderpass = RenderPass()
    def logic(self, dt):
        self.root.logic(dt)
        self.clean()
    def clean(self):
        if self.cleanup_list:
            for entity in self.cleanup_list:
                entity.cleanup()
            self.cleanup_list = []
    def transform_resource(self, *args, **kwargs):
        args = [self] + list(args)
        return args, kwargs
    def resolve_resource(self, *args, **kwargs):
        fn = filename_from_args(args, kwargs)
        assert fn
        fnl = fn.lower()
        for ext in ['.cson']:
            with open(fn, 'rb') as f:
                data = cson.load(f)
                if data['type'] == 'sprite':
                    return Sprite, args, kwargs
        for ext in ['.png','.jpg']:
            if fnl.endswith(ext):
                return Image, args, kwargs
        return None, None, None
    def render(self, time, dt):
        self.dt = dt
        self.time = time
        self.logic(dt)
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(gl.DEPTH_TEST | gl.CULL_FACE)
        if self.camera:
            self.root.render()
    def view_projection(self):
        return self.projection() * self.view()
    def projection(self):
        return self.camera.projection()
    def view(self):
        return self.camera.view()
    def matrix(self, m):
        self.shader['ModelViewProjection'] = flatten(
            self.view_projection() * m
        )

