#!/usr/bin/env python
from node import *
import numpy as np
from PIL import Image
import moderngl as gl
from defs import *

class Mesh(Node):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.vertices = None
    def load(self, fn):
        if type(self.vertices) == np.ndarray:
            img = Image.open(fn).convert('RGB')
            self.texture = self.ctx.texture(img.size, 3, img.tobytes())
            self.sampler = self.ctx.sampler(texture=self.texture)
            
            self.vbo = self.ctx.buffer(self.vertices.astype('f4').tobytes())
            self.vao = self.ctx.simple_vertex_array(self.app.shader, self.vbo, 'in_vert', 'in_text')

            self.vao.scope = self.ctx.scope(samplers=[
                self.sampler.assign(0),
            ])
    def render(self):
        self.app.shader['Model'] = flatten(self.transform)
        if self.visible:
            self.vao.render(self.mesh_type)

