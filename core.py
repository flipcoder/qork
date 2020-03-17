#!/usr/bin/env python
import glm
import moderngl_window as mglw
from itertools import chain

class Core(mglw.WindowConfig):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dtor = [] # nodes awaiting dtor/destuctor/deinit calls
        self.camera = None
    def logic(self, dt):
        self.root.logic(dt)
        self.clean()
        self.dtor = []
    def render(self, time, dt):
        self.time = time
        self.dt = dt
        self.logic(dt)
        self.ctx.clear(0.0, 0.0, 0.0)
        if self.camera:
            self.shader['Projection'] = tuple(chain(*self.camera.projection))
            self.shader['View'] = tuple(chain(*glm.inverse(self.camera.transform)))
            self.root.render()

