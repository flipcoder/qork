#!/usr/bin/python

from .resource import Resource


class Material(Resource):
    def __init__(self, tex):
        self.texture = tex
        pass

    def update(self, dt):
        pass

    def use(self, i=0):
        self.texture.use(i)
