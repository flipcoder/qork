# qork

MIT License
Copyright (c) 2020 Grady O'Connell

Qork is a (very new) python game framework built with ModernGL.

It is modeled after my C++ game engine, [Qor](https://github.com/flipcoder/qor).

I'm just getting started, so check back later!

## Features

- Scenegraph
- Resource Cache (ref-counted)
- Object Events
- State Machines
- Reactive Types (signals, reactive variables, observer-based lazy evaulation)
- Sprite Animation

## Install


### Linux

You can run the qork examples in place or install it using the setup file:

```
sudo python setup.py install
```

```

```

## Easy Mode Usage

Qork has a "zero mode", inspired by pygame-zero,
No boilerplate is required here, but you have to
run your program through the qork script instead of python.
You can use a shebang line if you want to execute it directly
on Linux and Mac or rename it to a .qork file and associate
that with qork on windows. This is optional.

Here's the shebang line:

```
#!/usr/bin/env qork
```

Let's load a player image and display it on the screen:

```
player = add('player.png')
```

Let's set the camera position:
camera.pos = (1,2,3)

Provide an x,y,z coordinate as a 2d or 3d tuple, or pyglm vec2/vec3 object.

A camera is automatically placed in the scene so that any spawned elements
will be visible by default.

Let's set the player velocity to the Y direction at a speed of 2

```
player.velocity = Y * 2
```

Or we could do this by changing the position every frame.  This is
what our automatically called update() function does.

```
def update(t):
    player.pos += Y * 2 * t
```

When you change position every frame instead of setting velocity,
remember to multiply it by t. This will allow for variable fps.
t is the time since the last frame in seconds (so it's a decimal number).
This will scale the movements to the amount they need to be to stay constant.

That's the entire script!  Run it with qork.

## Advanced Usage

To make your own object classes, inherit from Mesh:

```
class Player(Mesh):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.data = TEXTURED_QUAD_CENTERED
        self.load('data/player.cson') # spritesheet
        self.move(vec3(12,1,-10))
        self.scale(1.5)

class Map(Mesh):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.data = TEXTURED_QUAD
        self.load('data/map.png')
        self.rotate(0.25, vec3(-1,0,0))
        self.scale(100)

```

Spritesheet example (cson format):
```
type: 'sprite'
size: [ 16, 16 ]
tile_size: [ 16, 16 ]
origin: [ 0.5, 0.75 ]
mask: [ 0.25, 0.5, 0.75, 1.0 ]
states: ['life', 'direction', 'stance']
animation:
    speed: 10.0
    frames:
        alive:
            down:
                stand: ['default',0]
                walk: [0,1,0,2]
            up:
                stand: [3]
                walk: [3,4,3,5]
            left:
                stand: [6]
                walk: [6,7,6,8]
            right:
                stand: ['hflip',6]
                walk: ['hflip',6,7,6,8]
        dead: ['once',9,10,11]

```


Make some nodes and attach them:
```
add(Map())
player = add(Player())
camera = player.add(Camera())
camera.position(vec3(0,2,5))
```

More to come soon!  Work in progress!

