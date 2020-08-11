#!/usr/bin/env python

# import python_shader as gpu
# from python_shader import python2shader as shader

# vp, fp
SHADER_BASIC = {
    "vertex_shader": """
    #version 330
    
    uniform mat4 ModelViewProjection;
    
    in vec3 in_vert;
    in vec2 in_text;

    out vec2 v_text;

    void main() {
        gl_Position = ModelViewProjection * vec4(in_vert, 1.0);
        v_text = in_text;
    }
""",
    "fragment_shader": """
    #version 330
    
    uniform sampler2D Texture;

    in vec2 v_text;

    out vec4 f_color;

    void main() {
        vec4 t = texture(Texture, v_text);
        if(t.a < 0.95)
            discard;
        else {
            t.a = 0.0;
            f_color = t;
        }
    }
""",
}

from qork.util import DUMMY

class Shader:
    cache = {} # dict of programs with normalized ID
    def __init__(self, vp=None, fp=None):
        if vp is None and fp is None:
            self.vp = SHADER_BASIC['vertex_shader']
            self.fp = SHADER_BASIC['fragment_shader']
            self.name = 'BASIC'
        else:
            self.vp = vp
            self.fp = fp
            self.name = ''
        self.props = {}
    
    def define(self, prop, val=DUMMY):
        self.props[prop] = val
        if type(val) is bool:
            val = "true" if val else "false" # glsl bools
        self.fp = '#define ' + prop + ((' ' + val) if val is not DUMMY else '')

# @shader
# def vertex_basic(
#     ModelViewProjection: ('uniform', 'ModelViewProjection', gpu.mat4),
#     in_vert: ('input', 'in_vert', gpu.vec3),
#     in_text: ('input', 'in_text', gpu.vec2),
#     v_text: ('output', 'v_text', gpu.vec2),
#     gl_Position: ('output', 'gl_Position', gpu.vec2)
# ):
#     gl_Position = ModelViewProjection * vec4(in_vert, 1.0)
#     v_text = in_text

# @shader
# def fragment_basic(
#     texture: ('uniform', 'Texture', ''),
#     in_text: ('input', 'in_text', gpu.vec2),
#     f_color: ('output', 'f_color', gpu.vec4),
#     gl_Position: ('output', 'gl_Position', gpu.vec2)
# ):
#     t = texture(texture, v_text)
#     # if t.a < 0.75:
#     #     return
#     # else:
#     f_color = t

# SHADER_PYTHON_BASIC = {
#     "vertex_shader": vertex_basic,
#     "fragment_shader": fragment_basic
# }
