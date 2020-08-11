#!/usr/bin/env qork

camera.mode = '3D'
camera.z += 2
camera.fov = .12
sz = 0.5

skybox.add('sky.png', scale=vec3(vec2(Q.aspect_ratio, 1)*2,1))
canvas.text('This is a cube!')

gfx = 'box.png'

cube = add(Mesh(gfx, data=Prefab.cube()))
cube.z -= 1.5

def update(t):
    v = vec3(key(KEY.F) - key(KEY.S), key(KEY.SPACE) - key(KEY.A), key(KEY.D) - key(KEY.E))
    v = vec3(camera.matrix * vec4(v,0))
    camera.vel = v
    camera.rotate((key(KEY.LEFT) - key(KEY.RIGHT)) * t * 0.25, Y)
    
    cube.rotate(t * 0.4, -Y)

