#!/usr/bin/env python
import os
import numpy as np
import moderngl
import moderngl_window as mglw
import glm
from glm import vec3, mat4, normalize
from PIL import Image
from copy import copy

from reactive import *
from node import *
from component import *
from mesh import *
from camera import *
from core import *
from defs import *

class Player(Mesh):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.vertices = copy(QUAD)
        self.mesh_type = gl.TRIANGLE_STRIP
        self.load('data/player.cson')
        self.position(vec3(12,0,-10))
        self.scale(1.5)

class Map(Mesh):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.vertices = copy(QUAD)
        self.mesh_type = gl.TRIANGLE_STRIP
        self.load('data/map.png')
        self.rotate(0.25, vec3(-1,0,0))
        self.position(vec3(0,0,0))
        self.scale(100)
    
class App(Core):
    gl_version = (3, 3)
    title = "ModernGL Workbench"
    window_size = (960, 540)
    aspect_ratio = 4 / 3
    resizable = True
    samples = 4
    resource_dir = os.path.normpath(os.path.join(__file__, '../data/'))

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.btns = [False] * MAX_BUTTONS
        self.bg_color = (.25, .5, 1)
        
        self.shader = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform mat4 Model;
                uniform mat4 View;
                uniform mat4 Projection;
                
                in vec3 in_vert;
                in vec2 in_text;

                out vec2 v_text;

                void main() {
                    gl_Position = Projection * View * Model * vec4(in_vert, 1.0);
                    v_text = in_text;
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D Texture;

                in vec2 v_text;

                out vec4 f_color;

                void main() {
                    vec4 t = texture(Texture, v_text);
                    if(t.a < 0.9)
                        discard;
                    else
                        f_color = t;
                }
            ''',
        )

        self.root = Node(self)
        self.root.attach(Map(self))
        self.player = self.root.attach(Player(self))
        self.camera = self.root.attach(Camera(self))
        # self.camera = self.player.attach(Camera(self))
        self.camera.position(vec3(13,5,0))
        
    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        if action == keys.ACTION_PRESS:
            if key == keys.S:
                self.btns[LEFT] = True
            elif key == keys.F:
                self.btns[RIGHT] = True
            elif key == keys.E:
                self.btns[UP] = True
            elif key == keys.D:
                self.btns[DOWN] = True
            elif key == keys.A:
                self.btns[CROUCH] = True
            elif key == keys.SPACE:
                self.btns[JUMP] = True
            elif key == keys.J:
                self.btns[TURN_LEFT] = True
            elif key == keys.L:
                self.btns[TURN_RIGHT] = True
        if action == keys.ACTION_RELEASE:
            if key == keys.S:
                self.btns[LEFT] = False
            elif key == keys.F:
                self.btns[RIGHT] = False
            elif key == keys.E:
                self.btns[UP] = False
            elif key == keys.D:
                self.btns[DOWN] = False
            elif key == keys.A:
                self.btns[CROUCH] = False
            elif key == keys.SPACE:
                self.btns[JUMP] = False
            elif key == keys.J:
                self.btns[TURN_LEFT] = False
            elif key == keys.L:
                self.btns[TURN_RIGHT] = False
    
    def logic(self, dt):
        control = self.camera

        # move
        v = normalize(vec3(
            (-1 if self.btns[LEFT] else 0) +
            (1 if self.btns[RIGHT] else 0),
            (-1 if self.btns[CROUCH] else 0) +
            (1 if self.btns[JUMP] else 0),
            (-1 if self.btns[UP] else 0) +
            (1 if self.btns[DOWN] else 0)
        )) * 20
        v = (vec4(v,1.0) * glm.inverse(control.matrix(WORLD))).xyz
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

