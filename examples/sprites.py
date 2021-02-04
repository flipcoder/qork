#!/usr/bin/env qork
# FONT = './data/PressStart2P-Regular.ttf:64'
# canvas.font(FONT)

# def script(ctx):
#     canvas.text('Welcome.', anchor='', align='l')

player = add('spirit.cson', scale=1/8)
player.state["stance"] = "walk"

scale = 100
rocks = add('rocks.png',scale=100)
rocks.fork(geometry=True)
rocks.material.texture.repeat_x = rocks.material.texture.repeat_y = True
rocks.material.texture.filter = (gl.NEAREST, gl.NEAREST)
rocks.resources[0].scale_texture(8 * scale)

for i in range(5):
    for j in range(5):
        tile = Canvas(res=(1,1))
        tile.clear('white')

def update(dt):
    speed = 0.5
    v = vec3(key(KEY.RIGHT) - key(KEY.LEFT), key(KEY.UP) - key(KEY.DOWN), 0)
    v = glm.normalize(v)

    if v.x > EPSILON:
        player.state["direction"] = "right"
    elif v.x < -EPSILON:
        player.state["direction"] = "left"

    player.state["stance"] = "walk" if glm.length(v) > EPSILON else "stand"

    camera.vel = player.vel = v
    # player.vel = v

