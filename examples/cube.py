#!/usr/bin/env qork

# Q.virtual_resolution(100,100)
# Q.canvas.clear('red')

Q.camera.mode = "3D"
Q.camera.z += 2
Q.camera.fov = 0.12
sz = 0.5

Q.backdrop.add("sky.png", scale=Q.scale)
Q.canvas.ctext("Cube", shadow=True)

ground = Q.add(Canvas(color="green", scale=Q.scale))
ground.scale(25)
ground.z -= 1.5
ground.y -= 1
ground.rotate(-0.25, X)

cube = Q.add(Mesh.cube("box.png"))
cube.z -= 1.5
cube.spin(0.4, -Y)


def update(t):
    v = vec3(
        Q.key(KEY.F) - Q.key(KEY.S),
        Q.key(KEY.SPACE) - Q.key(KEY.A),
        Q.key(KEY.D) - Q.key(KEY.E),
    )
    # v = vec3(Q.camera.matrix * vec4(v,0))
    v = Q.camera.orient_parent_to_local(v)
    Q.camera.vel = v
    Q.camera.rotate((Q.key(KEY.LEFT) - Q.key(KEY.RIGHT)) * t * 0.25, Y)
    # Q.camera.rotate((key(KEY.UP) - key(KEY.DOWN)) * t * 0.25, X)
