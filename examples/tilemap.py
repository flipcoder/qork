#!/usr/bin/env qork

# from pprint import pp

console = False
camera.mode = "3D"
camera.z = 1

add("test.tmx")

# pp(scene.tree('p'))

t = 0
def update(dt):
    global t
    
    camera.vel = (
        key(KEY.RIGHT) - key(KEY.LEFT),
        key(KEY.UP) - key(KEY.DOWN),
        key(KEY.ENTER) - key(KEY.SPACE)
    )
    # print(camera.pos)
    
    t += dt

