#!/usr/bin/env qork

camera.position = (0, 0, 20)
player = add("player.png")
level = add("map.png")
level.scale(30)
# level.pos = Z * -10
# level.vel = Z * 5
# player.vel = -Z
camera.velocity = -X * 100


def update(t):
    if camera.position.z < 0:
        return quit()
    # print(camera.position)
    camera.view.pend()
    player.rotate(-t * 0.1)
    camera.rotate(t * 0.1)
