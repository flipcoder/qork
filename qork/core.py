#!/usr/bin/env python
import glm
import sys
# if __debug__:
#     sys.argv += ['--vsync','off']
import moderngl as gl
import moderngl_window as mglw
from .corebase import *
from .sprite import *
from .defs import *
from .cache import *
from .util import *
from .node import *
from .mesh import *
from .reactive import *
from .zero import qork_app
import cson
import os
from os import path

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
    # resource_dir = os.path.normpath(os.path.join(__file__, '../../data/'))
    
    def data_path(self, p=None):
        if p is None:
            return self._data_path
        folder = self.script_path or sys.argv[0]
        self._data_path = path.join(path.dirname(path.realpath(folder)),p)
        return self._data_path
    
    @classmethod
    def run(cls):
        mglw.run_window_config(cls)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.script_path = None # script path is using script
        qork_app(self)
        self.cache = Cache(self.resolve_resource, self.transform_resource)
        self._data_path = None
        self.data_path('data')
        self.on_resize = Signal()
        self.cleanup_list = [] # nodes awaiting dtor/destuctor/deinit calls
        self.root = Node()
        self.camera = None # default 3d camera
        self.gui = None # default 3d camera
        self.bg_color = (0,0,0)
        self.view_projection = Lazy(lambda: self.projection() * self.view())
        # self.renderpass = RenderPass()
        # self.Entity = Factory(self.resolve_entity)
        self.renderfrom = self.camera
        self.states = [] # stack
    def Entity(self, *args, **kwargs):
        if args and isinstance(args[0], Node):
            return args[0]
        fn = filename_from_args(args, kwargs)
        if fn:
            return Mesh(*args, *kwargs)
        elif isinstance(args[0], tuple): # prefab data
            return Mesh(*args, *kwargs)
        else:
            return Node(*args, *kwargs)
    def add(self, node):
        return self.root.add(node)
    def update(self, t):
        if t <= 0.0:
            return
        self.root.update(t)
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
            with open(path.join(self.data_path(), fn), 'rb') as f:
                data = cson.load(f)
                if data['type'] == 'sprite':
                    return Sprite, args, kwargs
        for ext in ['.png','.jpg']:
            if fnl.endswith(ext):
                return Image, args, kwargs
        return None, None, None
    def render(self, time, dt):
        if dt < 0.0:
            return
        self.dt = dt
        self.time = time
        self.update(dt)
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(gl.DEPTH_TEST | gl.CULL_FACE)
        if self.camera:
            self.renderfrom = self.camera
            self.view_projection.pend()
            self.root.render()
        if self.gui:
            self.renderfrom = self.gui
            self.view_projection.pend()
            self.gui.render()
        self.renderfrom = None
    # def view_projection(self):
    #     return self.projection() * self.view()
    def projection(self):
        return self.renderfrom.projection()
    def view(self):
        return self.renderfrom.view()
    def matrix(self, m):
        self.shader['ModelViewProjection'] = flatten(
            self.view_projection() * m
        )

