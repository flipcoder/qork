#!/usr/bin/env qork

from pprint import pp

console(False)
camera.mode = "2D"
scale = 0.2
# camera.z = 1

m = add("modern.tmx", pos=-Z, scale=scale)

# for i, c in enumerate(m):
#     c["batch"].children_visible = False
# m['ground']['batch'].children_visible = True
# m['ground decal']['batch'].children_visible = True
# m['middle']['batch'].children_visible = True
# m['middle decal']['batch'].children_visible = True
# m['middle under']['batch'].children_visible = True
# m['roof']['batch'].children_visible = True
# pp(scene.tree("p"))

player = add('player.cson', scale=scale)

t = 0

def update(dt):
    v = vec3(key(KEY.RIGHT) - key(KEY.LEFT), key(KEY.UP) - key(KEY.DOWN), 0)
    v *= scale * 5
    
    if v.y < -EPSILON:
        player.material.state('direction', 'down')
    elif v.y > EPSILON:
        player.material.state('direction', 'up')
    elif v.x > EPSILON:
        player.material.state('direction', 'right')
    elif v.x < -EPSILON:
        player.material.state('direction', 'left')

    if glm.length(v) > EPSILON:
        player.material.state('stance', 'walk')
    else:
        player.material.state('stance', 'stand')
    
    camera.vel = v
    player.vel = v

