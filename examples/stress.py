#!/usr/bin/env qork

cc = 306
objs = add(500, 'player.png', scale=0.1)
c = int(cc ** .5)
for i, obj in enumerate(objs):
    obj.pos = (i / c * 0.1, i % c * 0.1, 0)
    obj.spin(i * 0.0001 * i)

camera.mode = '3D'
# camera.x = 1
# camera.y = .5
camera.z = 2

def update(t):
    v = vec3(key(KEY.F) - key(KEY.S), key(KEY.SPACE) - key(KEY.A), key(KEY.D) - key(KEY.E))
    # v = vec3(camera.matrix * vec4(v,0))
    v = camera.orient_parent_to_local(v)
    camera.vel = v
    camera.rotate((key(KEY.LEFT) - key(KEY.RIGHT)) * t * 0.25, Y)

