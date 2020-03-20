#!/usr/bin/env python
import os
import numpy as np
import moderngl
import moderngl_window as mglw
import glm
from glm import vec3, mat4, normalize
from PIL import Image
from copy import copy
from qork import *

class Player(Mesh):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.data = TEXTURED_QUAD_CENTERED
        self.mesh_type = gl.TRIANGLE_STRIP
        self.filter = (gl.NEAREST, gl.NEAREST)
        self.load('data/player.cson')
        self.move(vec3(12,1,-10))
        self.scale(1.5)
        self.states({
            'life': 'alive',
            'stance': 'stand',
            'direction': 'up'
        })

class Map(Mesh):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.data = TEXTURED_QUAD
        self.mesh_type = gl.TRIANGLE_STRIP
        self.filter = (gl.NEAREST, gl.NEAREST)
        self.load('data/map.png')
        self.rotate(0.25, vec3(-1,0,0))
        self.scale(100)

class App(Core):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.btns = [False] * MAX_BUTTONS
        self.bg_color = (.25, .5, 1)
        self.shader = self.ctx.program(**SHADER_BASIC)

        self.root = Node(self)
        self.root.attach(Map(self))
        self.player = self.root.attach(Player(self))
        # self.camera = self.root.attach(Camera(self))
        self.camera = self.player.attach(Camera(self))
        self.camera.position(vec3(0,2,5))
        # self.camera.position(vec3(13,5,0))
        
        self.keybinds = [
            'S',
            'F',
            'E',
            'D',
            'SPACE',
            'A',
            'J',
            'L'
        ]

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        if action == keys.ACTION_PRESS:
            i = 0
            for bind in self.keybinds:
                if key == getattr(keys, bind):
                    self.btns[i] = True
                    break
                i += 1
        elif action == keys.ACTION_RELEASE:
            i = 0
            for bind in self.keybinds:
                if key == getattr(keys, bind):
                    self.btns[i] = False
                    break
                i += 1
    
    def logic(self, dt):
        control = self.player

        # move
        v = normalize(vec3(
            (-1 if self.btns[LEFT] else 0) +
            (1 if self.btns[RIGHT] else 0),
            (-1 if self.btns[CROUCH] else 0) +
            (1 if self.btns[JUMP] else 0),
            (-1 if self.btns[UP] else 0) +
            (1 if self.btns[DOWN] else 0)
        )) * 20
        v = (vec4(v,1.0) * glm.inverse(self.camera.matrix(WORLD))).xyz
        v.y *= 0.5
        control.velocity(v)
        
        # turn
        if self.btns[TURN_LEFT] or self.btns[TURN_RIGHT]:
            control.rotate(
                -dt * (
                    (-1.0 if self.btns[TURN_LEFT] else 0.0) +
                    (1.0 if self.btns[TURN_RIGHT] else 0.0)
                ) * 0.5,
                vec3(0,1,0)
            )

        super().logic(dt)

    def render(self, time, dt):
        super().render(time, dt)

if __name__ == '__main__':
    App.run()

