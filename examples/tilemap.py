#!/usr/bin/env qork

from pprint import pp

console(False)
camera.mode = "2D"
# camera.z = 1

m = add("modern.tmx", pos=-Z, scale=.05)
m['roof']['batch'].children_visible = False

pp(scene.tree('p'))

t = 0
def update(dt):
    global t
    
    camera.vel = (
        key(KEY.RIGHT) - key(KEY.LEFT),
        key(KEY.UP) - key(KEY.DOWN),
        0
    )
    
    t += dt

