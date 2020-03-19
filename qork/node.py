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
        def calculate_world_matrix():
            if self.parent:
                return self.parent.matrix(WORLD) * self.transform
            else:
                return self.transform
        self.world_transform = Lazy(calculate_world_matrix)
        self.components = []
        self.detach_me = []
        self.deinited = False
        self.on_deinit = Signal()
        self.on_detach = Signal()
        self.on_event = Signal()
        self.vel = vec3(0)
        self.accel = vec3(0)
        self.being_destroyed = False # scheduled to be destroyed?
        self.destroyed = False
    def pend(self):
        self.world_transform.pend()
    def event(self, *args, **kwargs):
        self.on_event(*args, **kwargs)
    def __call__(self, *args, **kwargs):
        self.event(*args, **kwargs)
    def matrix(self, space = PARENT):
        assert space != LOCAL
        if space==PARENT:
            return self.transform
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
        if v == None: # get
            if space == PARENT:
                return self.world_transform()[3].xyz
            elif space == WORLD:
                return vec3(self.world_transform()[3].xyz)
            assert False
        assert space == PARENT # other spaces are not yet impl
        self.transform[3] = vec4(v, 1.0) # set
        self.pend()
    def move(self, v: vec3):
        self.transform[3] += vec4(v, 0.0)
        self.pend()
    def pend(self):
        self.world_transform.pend()
        for ch in self.children:
            ch.pend()
    def attach(self, node):
        assert not node.parent
        self.children.append(node)
        node.parent = self
        return node
        self.pend()
    def logic(self, dt):
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
            detach_me = self.detach_me
            self.children = list(filter(lambda x: x not in detach_me, self.children))
            self.detach_me = []
            for node in detach_me:
                node.on_detach(node)
    def destroy(self):
        if not self.being_destroyed:
            self.detach()
            self.app.cleanup_list.append(self) # schedule Core to cal clean()
            self.destroyed = True
    def safe_detach(self, func = None):
        if self.parent:
            self.parent.detach_me.append(self)
            if func:
                self.on_detach.connect(func)
    def detach(self, node=None):
        if node == None: # detach self
            self.parent.children = list(filter(lambda x: x != self, self.parent.children))
            self.on_detach()
            self.parent = None
            self.pend()
        else:
            assert node.parent == self
            node.detach()
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

