#!/usr/bin/env qork

img = "player.png"

Q.camera.mode = "3D"
Q.camera.z = 1

p = Q.add(img)

level = Q.add("map.png", scale=25, pos=-Z * 10)

nodes = [None] * 4
nodes[0] = p.add(img, scale=0.25, pos=(-0.5, 0.5, 0.1))
nodes[1] = p.add(img, scale=0.25, pos=(0.5, -0.5, 0.1))
nodes[2] = p.add(img, scale=0.25, pos=(-0.5, -0.5, 0.1))
nodes[3] = p.add(img, scale=0.25, pos=(0.5, 0.5, 0.1))

t = 0


def update(dt):
    global t
    t += dt
    camera.pos = (0, 0, 2 + 0.5 * sint(t) + 1)
    p.rotate(dt * 0.1)
    for i, n in enumerate(nodes):
        n.z = 1 + 0.5 * sint(t)
        n.rotate(dt * i * 0.1)
        n.rotate(dt, X)

    Q.camera.reset_orientation()
    Q.camera.rotate(0.01 * sint(t / 2), Y)
