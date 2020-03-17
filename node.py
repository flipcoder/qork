#!/usr/bin/env python
import glm
import math
from reactive import Signal
from glm import vec3, mat4

class Node:
    LOCAL = 0
    PARENT = 1
    WORLD = 2
    def __init__(self, app, **kwargs):
        self.app = app
        self.ctx = app.ctx
        self.visible = True
        self.self_visible = True
        self.children = []
        self.parent = None
        self.transform = mat4(1.0)
        self.components = []
        self.detach_me = []
        self.deinited = False
        self.on_deinit = Signal()
        self.on_detach = Signal()
        self.vel = None
    def rotate(self, turns, axis):
        self.transform *= glm.rotate(turns * 2.0 * math.PI, axis)
    def velocity(self, v = None):
        if not v:
            return self.vel
        self.vel = v
    def position(self, v = None, space = None):
        if type(v) == int and space==None:
            space = v
            v = None
        if not v:
            return vec3(
                self.transform[3][0],
                self.transform[3][1],
                self.transform[3][2]
            )
        self.transform[3][0] = v.x
        self.transform[3][1] = v.y
        self.transform[3][2] = v.z
    def move(self, v: vec3):
        self.transform[3][0] += v.x
        self.transform[3][1] += v.y
        self.transform[3][2] += v.z
    def attach(self, node):
        self.children.append(node)
        node.parent = self
    def logic(self, dt):
        self.detach_me = []
        for component in self.components:
            self.components.logic(self, dt)
        for ch in self.children:
            ch.logic(dt)
        if self.detach_me:
            self.children = filter(lambda x: x not in self.detach_me, children)
            self.detach_me = []
        if self.vel:
            self.position(self.position() + (self.vel * dt))
    def detach(self):
        if self.parent:
            self.parent.detach_me.append(self)
        self.on_detach()
        self.app.dtor.append(self)
    def render(self):
        if self.visible:
            for component in self.components:
                self.components.render(self, dt)
            for ch in self.children:
                ch.render()
    def deinit(self):
        if not self.deinited:
            self.on_deinit()
            for ch in self.children:
                ch.deinit()
            self.deinited = True

