#!/usr/bin/env python
import glm
import math
from .reactive import *
from glm import vec3, vec4, mat4
from .defs import *

class Node:
    def __init__(self, app, **kwargs):
        self.app = app
        self.ctx = app.ctx
        self.visible = True
        self.self_visible = True
        self.children = []
        self.parent = None
        self.transform = mat4(1.0)
        def world_calc(self):
            if self.parent:
                return self.parent.matrix(WORLD) * self.transform
            else:
                return self.transform
        self.world_transform = Lazy(lambda _, self=self: world_calc(self))
        self.components = []
        self.detach_me = []
        self.deinited = False
        self.on_deinit = Signal()
        self.on_detach = Signal()
        self.vel = vec3(0)
        self.accel = vec3(0)
        self.being_destroyed = False # scheduled to be destroyed?
        self.destroyed = False
    def pend(self):
        self.world_transform.pend()
    def matrix(self, space = PARENT):
        assert space != LOCAL
        if space==PARENT:
            return self.transform
        # else: # WORLD
        return self.world_transform()
    def rotate(self, turns, axis):
        self.transform = glm.rotate(self.transform, turns * 2.0 * math.pi, axis)
        self.world_transform.pend()
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
            self.transform *= glm.scale(mat4(1.0), v)
        elif space == PARENT:
            self.transform = glm.scale(mat4(1.0), v) * self.transform
        else:
            assert False # not impl
        self.world_transform.pend()
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
        self.world_transform.pend()
    def move(self, v: vec3):
        self.transform[3] += vec4(v, 0.0)
        self.world_transform.pend()
    def attach(self, node):
        assert not node.parent
        self.children.append(node)
        node.parent = self
        return node
        self.world_transform.pend()
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
    def destroy(self):
        if not self.being_destroyed:
            self.detach()
            self.app.cleanup_list.append(self) # schedule Core to cal clean()
            self.destroyed = True
    def detach(self):
        if self.parent:
            self.parent.detach_me.append(self)
        self.world_transform.pend()
        self.on_detach()
    def render(self):
        if self.visible:
            for component in self.components:
                self.components.render(self)
            for ch in self.children:
                ch.render()
    def clean(self): # called by Core as an explicit destructor
        if not self.deinited:
            self.on_deinit()
            for ch in self.children:
                ch.deinit()
            self.deinited = True

