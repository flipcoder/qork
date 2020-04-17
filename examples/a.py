#!/usr/bin/env qork

camera.ortho = True
# camera.pos = (0,0,1)
p = add("player.png")
t = 1


def update(dt):
    global t
    t += dt
    p.reset_scale()
    p.scale(1 + t)
    # camera.z = t
    qork_app().view_projection.pend()
    # print(camera.z)
