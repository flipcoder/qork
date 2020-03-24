#!/usr/bin/env qork

camera.pos = (0,0,5)
player = add('player.png')
level = add('map.png')
level.scale(10)
level.pos = Z * -10
level.vel = Z
camera.vel = -Z

def update(t):
    if camera.position.z < level.position.z:
        print('You hit the ground!')
        return quit()
    player.rotate(t * 0.1)
    camera.rotate(t * 0.1)

