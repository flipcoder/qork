#!/usr/bin/env qork

camera.mode = "3D"
camera.z += 2
camera.fov = 0.12
sz = 0.5

Q.backdrop.add("sky.png", scale=Q.scale)
canvas.text("Cube", shadow=True)

ground = add(Canvas(color="green", scale=Q.scale))
ground.scale(25)
ground.z -= 1.5
ground.y -= 1
ground.rotate(-0.25, X)

cube = add(Mesh.cube("box.png"))
cube.z -= 1.5
cube.spin(0.4, -Y)


def update(t):
    v = vec3(
        key(KEY.F) - key(KEY.S), key(KEY.SPACE) - key(KEY.A), key(KEY.D) - key(KEY.E)
    )
    # v = vec3(camera.matrix * vec4(v,0))
    v = camera.orient_parent_to_local(v)
    camera.vel = v
    camera.rotate((key(KEY.LEFT) - key(KEY.RIGHT)) * t * 0.25, Y)
    # camera.rotate((key(KEY.UP) - key(KEY.DOWN)) * t * 0.25, X)
