#!/usr/bin/env qork

console = False

camera.mode = '3D'
camera.z = 1.5

bg = add(Canvas(scale=vec3(app.aspect_ratio,1,0)*10, pos=-Z))
grad = cairo.LinearGradient(0, 0, *bg.res)
grad.add_color_stop_rgb(0, 0, 0, 0)
grad.add_color_stop_rgb(1, .4, .4, .4)
bg.spin(-.2)
bg.set_source(grad)
bg.paint()

nodes = [None] * 2
for i in range(len(nodes)):
    n = nodes[i] = add(Canvas(scale=(app.aspect_ratio,1)))
    n.font(n.res[0]/5)

nodes[0].text('Hello', nodes[0].res/2, 'red')
nodes[0].x = -.5
nodes[1].text('World', nodes[1].res/2, 'blue')
nodes[1].x = .5

def update(dt):
    for i, n in enumerate(nodes):
        s = (1 + i) * 0.2
        n.rotate(s * 0.1 * dt, X)
        n.rotate(s * 0.2 * dt, Y)
        n.rotate(s * 0.3 * dt, Z)

