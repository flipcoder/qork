#!/usr/bin/env qork
FONT = './data/PressStart2P-Regular.ttf:64'
canvas.font(FONT)

def script(ctx):
    canvas.text('Health: |||||', anchor='', align='l')

player = add("spirit.cson", scale=1 / 16)
player.state["stance"] = "walk"
player.rotate(.125,X)
player.z = 1 / 16
camera.fov = .09
player.y = 2.5 / 16

camera.mode = '3D'
camera.y = -.5
camera.z = 1

scale = 5
rocks = add("rocks.png", scale=scale)
rocks.fork(geometry=True)
rocks.material.filter(False)
rocks.material.repeat(True)
rocks.resources[0].scale_texture(8 * scale)

camera.rotate(.1, X)

def make_cube(pos):
    cube = add(Mesh.cube("box.png"))
    cube.material.filter(False)
    cube.scale(.1)
    cube.pos = vec3(pos[0], pos[1], .5 * .1)
    return cube

for i in range(-10, 10):
    for j in range(-10, 10):
        if random.random() < 0.1:
            make_cube((i/10,j/10))

for i in range(5):
    for j in range(5):
        tile = Canvas(res=(1, 1))
        tile.clear("white")

player.dir = vec3(1,0,0)

def update(dt):
    speed = 0.5
    v = vec3(key(KEY.RIGHT) - key(KEY.LEFT), key(KEY.UP) - key(KEY.DOWN), 0)
    v = glm.normalize(v)

    if v.x > EPSILON:
        player.state["direction"] = "right"
    elif v.x < -EPSILON:
        player.state["direction"] = "left"

    player.state["stance"] = "walk" if glm.length(v) > EPSILON else "stand"

    if key_pressed(KEY.SPACE):
        bullet = add('spirit.png', pos=player.pos, scale=0.02, lifetime=1)
        bullet.material.filter(False)
        bullet.vel = copy(player.dir) * 2

    if glm.length(player.vel) > EPSILON:
        player.dir = glm.normalize(player.vel)
    camera.vel = player.vel = v
    # player.vel = v

    # infinite rocks xy
    rocks.xy = (player.pos.xy // 1).xy

# @overlap(player, 'box.png')
# def player_cube(player, cube, dt):
#     pass

