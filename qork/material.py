#!/usr/bin/python

from .resource import Resource
import moderngl as gl


class Material(Resource):
    def __init__(self, tex=None, image=None):
        super().__init__()
        self.texture = tex
        self.image = None
        self.backfaces = False

    def update(self, dt):
        pass

    def repeat(self, b):
        self.texture.repeat_x = self.texture.repeat_y = b

    def filter(self, b):
        if b is True:
            self.texture.filter = (gl.LINEAR, gl.LINEAR)
        elif b is False:
            self.texture.filter = (gl.NEAREST, gl.NEAREST)
        else:
            self.texture.filter = b

    def use(self, i=0):
        if self.texture:
            self.texture.use(i)
