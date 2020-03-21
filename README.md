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

## Getting Started

Qork has a easy/zero mode, inspired by pygame-zero,
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

## Nodes

### Create and Add

```
node = create() # create an empty node without adding it to the scene

node = Node() # same as above

node = add() # create and add an empty node to the scene

node = add(Node()) # same as above

node = add('player.png') # create object based on image, and add to scene

```

### Positioning


Positioning can be set using either 3D or 2D tuples/lists or any unpackable type.
Internally, vec3 (from glm) is used.

```
node.position = (0,0) # 2D

node.position = vec2(0,0)
    
node.position = (0,0,0) # 3D
    
node.position = vec3(0,0,0)

node.move(1,2,3) # relative movement (changes position)
    
node.move(vec2(1,2))

node.move(vec3(1,2,3))

```

You can use `pos` instead of position if you prefer.

### Velocity/Acceleration

Global vectors X, Y and Z are basis vectors that point in that direction.

The below code will start node moving at 1unit/sec in the positive X

```
node.velocity = X

node.acceleration = Z

node.acceleration = (1,2) # 2d

node.acceleration = (1,2,3) # 3d

node.stop() # stops velocity and acceleration
```

You can use `vel` and `accel` if you prefer.

### Attaching

Nodes can be attached to another, so they are moved along with the parent.

```
parent = add()
child = parent.add()
```

Node positions are relative to their parents, so if you want to get
the real world position of a node, use `world_position`

```
print(child.world_position)
```

### Detaching

...

### Rotation/Scaling

Qork angles are based on **turns**. Rotating .5 is half a turn.

This will be changeable in the future.

This is similar to multiplying a value by 2*PI radians or 360 degrees.

```
node.rotate(.25) # rotate quarter turn in 2D

node.rotate(.5, Y) # rotate half turn in 3D around Y axis
```

The second parameter to rotate can take any vector.

## Camera

In easy/zero mode, the camera is a global called `camera`.

```
camera.position = (0,0,5) # back up the camera by 5 units

camera.fov = 80 # change field of view

camera.mode = '2D' # go into 2D mode (not yet implemented)
```

## Tags

...

## States

...

## Events

...

## Resource Cache

Resources are automatically cached for later reuse and reference counted.

## Reactive Classes

### Signal

...

### Reactive

...

### Lazy

...


## Custom Objects

To make your own object classes, inherit from Mesh:

```
class Map(Mesh):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.data = TEXTURED_QUAD
        self.load('data/map.png')
        self.rotate(0.25, vec3(-1,0,0))
        self.scale(100)

```

## Spritesheets

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

Load a spritesheet with add() and make it do the walk animation:

Note: This is not yet fully implemented.

```
player = add('player.cson')
player.state('stance','walk')
```

More to come soon!  Work in progress!

