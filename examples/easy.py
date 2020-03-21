#!/usr/bin/env qork
data_path('../data')

camera.pos = (0,0,5)
player = add('player.png')
camera.velocity = -Z

def update(t):
    print(player.position)

