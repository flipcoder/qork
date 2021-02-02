#!/usr/bin/env python

# import python_shader as gpu
# from python_shader import python2shader as shader
from qork.resource import Resource

SHADER_DEFS = ["fog"]

# vp, fp
SHADER_BASIC = {
    "vertex_shader": """
    #version 330
    
    uniform mat4 ModelViewProjection;
    
    in vec3 in_vert;
    in vec2 in_text;

    #ifdef FOG
        out vec3 v_vert;
    #endif
    out vec2 v_text;

    void main() {
        gl_Position = ModelViewProjection * vec4(in_vert, 1.0);
        #ifdef FOG
            v_vert = gl_Position.xyz;
        #endif
        v_text = in_text;
    }
""",
    "fragment_shader": """
    #version 330
    
    uniform sampler2D Texture;

    in vec2 v_text;

    #ifdef FOG
        in vec3 v_vert;
        uniform vec4 fog_color;
    #endif

    out vec4 f_color;

    void main() {
        vec4 t = texture(Texture, v_text);
        
        #ifdef FOG
            vec3 t2 = t.xyz * (1 / v_vert.z) * 2.0;
            for(int i=0;i<3;++i)
                t[i] = mix(t2[i], t[i], fog_color.a);
        #endif
        
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


class Shader(Resource):
    cache = {}  # dict of programs with normalized ID

    # def __init__(self, app):#vp=None, fp=None, defs={}):
    def __init__(self, app, name="", vp=None, fp=None, defs=None):
        super().__init__(app, name)
        self.dirty = True

        if vp is None and fp is None:
            self.vp = SHADER_BASIC["vertex_shader"]
            self.fp = SHADER_BASIC["fragment_shader"]
            self.version = "330"
            self.name = "BASIC"
        else:
            self.vp = vp
            self.fp = fp
            self.version = "330"
            self.name = ""

        self.props = {}

        if defs:
            for k, v in defs.items():
                if v is not False and v is not None:
                    self[k] = v

        # self.uniform = self.program = self.app.ctx.program(
        #     vertex_shader=self.vp, fragment_shader=self.fp
        # )
        self.compile()

    def instance(self, name, defs):
        s = Shader(self.app, name, self.vp, self.vp, defs)
        for key, val in defs.items():
            s[key] = val
        s.compile()
        return s

    def compile(self):
        if self.dirty:
            self.uniform = self.program = self.app.ctx.program(
                vertex_shader=self.vp, fragment_shader=self.fp
            )
            self.dirty = False
        return self.program

    def __setitem__(self, prop, val):
        # TODO: add in values pre-compile instead of into source

        if val is None:
            del self.props[prop]
        else:
            if type(val) is bool:
                val = "true" if val else "false"  # glsl bools
            else:
                val = str(val)

            self.props[prop] = val

        prop = prop.upper()

        p = {}
        for program in ("fp", "vp"):
            pp = self.__dict__[program].strip()
            version_line = pp[pp.index("#version") :].split("\n")[0]
            assert "#version" in version_line
            p[program] = pp = pp[pp.index("\n") :]
            p[program] = pp = (
                "#define " + prop + ((" " + val) if val is not DUMMY else "") + pp
            )
            if version_line:
                p[program] = pp = version_line + "\n" + pp

        self.fp = p["fp"]
        self.vp = p["vp"]
        self.dirty = True
        return self

    def __getitem__(self, prop):
        return self.props.get(prop)


class ShaderInstance(Resource):
    def __init__(self, app, shader, defs={}):
        pass


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
