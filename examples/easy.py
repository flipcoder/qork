#!/usr/bin/env qork

camera.pos = (0,0,5)
player = add('player.png')
camera.velocity = -Z

def update(t):
    print(camera.position)

