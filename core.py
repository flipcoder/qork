#!/usr/bin/env python
import glm
import moderngl as gl
import moderngl_window as mglw
from defs import *

class Core(mglw.WindowConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cleanup_list = [] # nodes awaiting dtor/destuctor/deinit calls
        self.camera = None
        self.bg_color = (0,0,0)
    def logic(self, dt):
        self.root.logic(dt)
        self.clean()
    def clean(self):
        if self.cleanup_list:
            for cleanup_list in self.cleanup_list:
                cleanup_list.cleanup()
            self.cleanup_list = []
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

