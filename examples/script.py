#!/usr/bin/env qork

camera.mode = '3D'
camera.position = (0, 0, 20)
player = add("player.png")
player.scale(3)
level = add("map.png")
level.scale(100)
level.pos = Z * -50
level.vel = Z * 20
player.vel = -Z


def update(t):
    if level.position.z > 0:
        return quit()
    player.rotate(-t * 0.1)
    camera.rotate(t * 0.1)
