#!/usr/bin/env python
import sys
sys.path.append('.')
sys.path.append('..')
import os
import numpy as np
import moderngl
import moderngl_window as mglw
import glm
from glm import vec3, mat4, normalize
from PIL import Image
from copy import copy
from qork import *
from qork.zero import *
import os
from os import path

class Player(Mesh):
    def __init__(self, *args, **kwargs):
        self.fn = 'player.cson'
        super().__init__(*args, **kwargs)
        self.data = TEXTURED_QUAD_CENTERED
        self.mesh_type = gl.TRIANGLE_STRIP
        self.filter = (gl.NEAREST, gl.NEAREST)
        self.move(vec3(12,1,-10))
        self.scale(1.5)
        self.states({
            'life': 'alive',
            'stance': 'stand',
            'direction': 'up'
        })

class Level(Mesh):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = TEXTURED_QUAD
        self.mesh_type = gl.TRIANGLE_STRIP
        self.filter = (gl.NEAREST, gl.NEAREST)
        self.load('map.png')
        self.rotate(0.25, vec3(-1,0,0))
        self.scale(100)

class App(Core):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_path('../data')
        
        self.btns = [False] * MAX_BUTTONS
        self.bg_color = (.25, .5, 1)
        self.shader = self.ctx.program(**SHADER_BASIC)

        self.level = self.root.add(Level(self))
        self.player = self.root.add(Player(self))
        self.camera = self.player.add(Camera(self))
        self.camera.position = (0,2,5)
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
    
    def update(self, dt):
        control = self.player

        # move
        v = vec3(
            (-1 if self.btns[LEFT] else 0) +
            (1 if self.btns[RIGHT] else 0),
            (-1 if self.btns[CROUCH] else 0) +
            (1 if self.btns[JUMP] else 0),
            (-1 if self.btns[UP] else 0) +
            (1 if self.btns[DOWN] else 0)
        )
        if glm.length(v) >= EPSILON:
            v = normalize(v) * 20
        else:
            v = vec3(0)
        
        v = (vec4(v,1.0) * glm.inverse(self.camera.matrix(WORLD))).xyz
        v.y *= 0.5
        control.velocity = v
        
        # turn
        if self.btns[TURN_LEFT] or self.btns[TURN_RIGHT]:
            control.rotate(
                -dt * (
                    (-1.0 if self.btns[TURN_LEFT] else 0.0) +
                    (1.0 if self.btns[TURN_RIGHT] else 0.0)
                ) * 0.5, Y
            )

        super().update(dt)

    def render(self, time, dt):
        super().render(time, dt)

if __name__ == '__main__':
    App.run()

