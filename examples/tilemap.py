#!/usr/bin/env qork

from pprint import pp

camera.mode = "2D"

sky = camera.add(Canvas("sky"))
sky.gradient(vec3(0.2, 0.4, 0.9), "white", region=(0, 0, 0, sky.res[1]))
sky.pos = -Z * 100
sky.scale(200)
scale = 0.125

m = add("modern.tmx", pos=-Z, scale=scale)

player = add("player.cson", scale=scale)
# player.pos = -Z * 0.895 * scale
player.pos = -Z * 0.7494
t = 0


def update(dt):
    speed = 0.5
    v = vec3(key(KEY.RIGHT) - key(KEY.LEFT), key(KEY.UP) - key(KEY.DOWN), 0)
    v = glm.normalize(v)

    if v.y < -EPSILON:
        player.state["direction"] = "down"
    elif v.y > EPSILON:
        player.state["direction"] = "up"
    elif v.x > EPSILON:
        player.state["direction"] = "right"
    elif v.x < -EPSILON:
        player.state["direction"] = "left"

    if key(KEY.SPACE):
        player.move(dt * Z * 0.0001)
        print(player.z)
    if key(KEY.A):
        player.move(dt * -Z * 0.0001)
        print(player.z)

    player.state["stance"] = "walk" if glm.length(v) > EPSILON else "stand"

    camera.vel = player.vel = v
