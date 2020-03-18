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
    def load(self, fn=None):
        if fn:
            img = Image.open(fn).convert('RGBA')
            self.texture = self.ctx.texture(img.size, 4, img.tobytes())
        if type(self.vertices) == np.ndarray:
            self.vbo = self.ctx.buffer(self.vertices.astype('f4').tobytes())
            self.vao = self.ctx.simple_vertex_array(self.app.shader, self.vbo, 'in_vert', 'in_text')
    def render(self):
        if self.visible:
            self.app.shader['Model'] = flatten(self.matrix(WORLD))
            self.texture.use()
            self.vao.render(self.mesh_type)
        super().render()

