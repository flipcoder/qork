#!/usr/bin/env qork

camera.mode = "3D"
camera.z = 1.5

backdrop.gradient("blue","lightblue","white","yellow","green","darkgreen")

nodes = [None] * 2
for i in range(len(nodes)):
    n = nodes[i] = add(Canvas())
    n.font(n.res[0] / 5)

nodes[0].text("Hello", "gray", shadow=True)
nodes[0].x = -0.3
nodes[1].text("World", "brown", shadow=True)
nodes[1].x = 0.3


def update(dt):
    for i, n in enumerate(nodes):
        s = (1 + i) * 0.2
        n.rotate(s * 0.1 * dt, X)
        n.rotate(s * 0.2 * dt, Y)
        n.rotate(s * 0.3 * dt, Z)

