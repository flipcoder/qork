#!/usr/bin/env python
from .util import *

class Animator:
    def __init__(self, node):
        self.node = node
        self.app = node.app
        sprite = self.sprite = node.sprite
        data = self.data = sprite.data
        self.animation = data['animation']
        self.frames = self.animation['frames']
        self.speed = self.animation['speed']
        
        self.frame = ([] * treedepth(self.frames))
    def update(self, t):
        pass
        # self.node.frame = int(self.app.time % 10)

