#!/usr/bin/env python
import glm
import math
from reactive import Signal
from glm import vec3, vec4, mat4
from defs import *

class Node:
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
        self.vel = vec3(0)
        self.accel = vec3(0)
        self.being_destroyed = False # scheduled to be destroyed?
        self.destroyed = False
    def rotate(self, turns, axis):
        self.transform = glm.rotate(self.transform, turns * 360, axis)
    def velocity(self, v = None):
        if v == None:
            return self.vel
        self.vel = v
    def accelerate(self, a):
        self.accel += a
    def acceleration(self, a = None):
        if a == None:
            return self.accel or vec3(0)
        self.accel = a
    def scale(self, v = None, space = LOCAL):
        if v == None:
            assert False #
        if type(v)==int or type(v)==float:
            v = vec3(float(v))
        if space == LOCAL:
            self.transform *= glm.scale(mat4(), v)
        elif space == PARENT:
            self.transform = glm.scale(mat4(), v) * self.transform
        else:
            assert False # not impl
    def position(self, v = None, space = None):
        if type(v) == int and space==None:
            space = v
            v = None
        if space==None:
            space = PARENT
        assert space == PARENT # other spaces are not yet impl
        if not v:
            return self.transform[3].xyz
        self.transform[3] += vec4(v, 0.0)
    def move(self, v: vec3):
        self.transform[3] += vec4(v, 0.0)
    def attach(self, node):
        assert not node.parent
        self.children.append(node)
        node.parent = self
    def logic(self, dt):
        self.detach_me = []
        for component in self.components:
            self.components.logic(self, dt)
        
        new_vel = None
        if self.accel != None:
            new_vel = vec3(0)
            self.vel += self.accel/2.0 * dt
        if glm.length(self.vel) > EPSILON: # velocity not zero
            self.move(self.vel * dt)
        if new_vel: # accelerated
            self.vel = new_vel

        for ch in self.children:
            ch.logic(dt)
        if self.detach_me:
            self.children = filter(lambda x: x not in self.detach_me, children)
            self.detach_me = []
    def cleanup(self): # called by Core as an explicit destructor
        pass
    def destroy(self):
        if not self.being_destroyed:
            detach()
            self.app.dtor.append(self) # schedule Core to call _destroy()
            self.detaching = True
    def detach(self):
        if self.parent:
            self.parent.detach_me.append(self)
        self.on_detach()
    def render(self):
        if self.visible:
            for component in self.components:
                self.components.render(self)
            for ch in self.children:
                ch.render()
    def deinit(self):
        if not self.deinited:
            self.on_deinit()
            for ch in self.children:
                ch.deinit()
            self.deinited = True

