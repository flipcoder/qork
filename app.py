#!/usr/bin/env python
import os
import numpy as np
import moderngl
import moderngl_window as mglw
import glm
from glm import vec3, mat4, normalize
from PIL import Image

from reactive import *
from node import *
from component import *
from mesh import *
from camera import *
from core import *
from defs import *

class Map(Mesh):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.vertices = np.array([
            # x    y    z    u    v
            0.0, 0.0, 0.0, 0.0, 1.0,
            1.0, 0.0, 0.0, 1.0, 1.0,
            0.0, 1.0, 0.0, 0.0, 0.0,
            1.0, 1.0, 0.0, 1.0, 0.0,
        ])
        self.mesh_type = gl.TRIANGLE_STRIP
        self.load('data/map.png')
    
class App(Core):
    gl_version = (3, 3)
    title = "ModernGL Workbench"
    window_size = (800, 600)
    aspect_ratio = 4 / 3
    resizable = True
    samples = 4
    resource_dir = os.path.normpath(os.path.join(__file__, '..'))

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.btns = [False] * 4 # left, right, up down
        
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
                    gl_Position = View * Model * Projection * vec4(in_vert, 1.0);
                    v_text = in_text;
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D Texture;

                in vec2 v_text;

                out vec4 f_color;

                void main() {
                    f_color = texture(Texture, v_text);
                }
            ''',
        )

        self.root = Node(self)
        self.root.attach(Map(self))
        self.camera = Camera(self)
        self.root.attach(self.camera)

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        if action == keys.ACTION_PRESS:
            if key == keys.LEFT:
                self.btns[LEFT] = True
            elif key == keys.RIGHT:
                self.btns[RIGHT] = True
            elif key == keys.UP:
                self.btns[UP] = True
            elif key == keys.DOWN:
                self.btns[DOWN] = True
        if action == keys.ACTION_RELEASE:
            if key == keys.LEFT:
                self.btns[LEFT] = False
            elif key == keys.RIGHT:
                self.btns[RIGHT] = False
            elif key == keys.UP:
                self.btns[UP] = False
            elif key == keys.DOWN:
                self.btns[DOWN] = False

    def logic(self, dt):
        self.camera.velocity(vec3(
            (-1 if self.btns[LEFT] else 0) +
            (1 if self.btns[RIGHT] else 0),
            0,
            (-1 if self.btns[UP] else 0) +
            (1 if self.btns[DOWN] else 0)
        ))
        if self.camera.velocity() != vec3(0):
            print(self.camera.position())
        super().logic(dt)

    def render(self, time, dt):
        super().render(time, dt)

if __name__ == '__main__':
    App.run()

