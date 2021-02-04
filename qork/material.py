#!/usr/bin/python

from .resource import Resource


class Material(Resource):
    def __init__(self, tex=None, image=None):
        super().__init__()
        self.texture = tex
        self.image = None
        self.backfaces = False

    def update(self, dt):
        pass

    def use(self, i=0):
        if self.texture:
            self.texture.use(i)
