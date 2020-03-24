#!/usr/bin/env python

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
        if(t.a < 0.75)
            discard;
        else
            f_color = t;
    }
""",
}
