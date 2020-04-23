# qork

MIT License. See LICENSE file for details.

Copyright (c) 2020 Grady O'Connell

Qork is a (very new) 3D/2D python OpenGL framework built with ModernGL and other libs.

It is designed to be extremely easy to use for gamejams, prototypes and full projects alike.

This is VERY NEW and some things are only partially implemented.
Features will change.  This is not yet stable enough for production.

## Features

- Live coding
- Scenegraph
- Resource Cache
- Reactive Types (signals, reactive variables, observer-based lazy evaluation)
- Object Events
- State Machines
- Sprite Animation (PARTIAL)

## Integration

- glm
- pillow
- CSON
- cairo (pyCairo) (PARTIAL)
- bullet (SOON)
- OpenAL (python-openal) (SOON)
- pytweening (SOON)

## Running Locally (no installation)

If you haven't already, download qork and enter the qork folder:

```
git clone https://github.com/flipcoder/qork
cd qork
```

Make sure you have a new version of python 3.  Qork does not work with Python 2.

Get dependencies:

```
sudo pip install -r requirements.txt
```

(Example images are not yet included! You can use your own images. I will fix this soon!)

Make examples executable and run any example:

```
chmod +x ./examples/*.py
./qork.py examples/script.py
```

## Installation

If you haven't already, download qork and enter the qork folder:

```
git clone https://github.com/flipcoder/qork
cd qork
```

If you wish to install qork, simply run:

```
sudo python setup.py install
```

After installation, on unix systems, you should be able to run qork
applications and scripts if you mark them as executable:

```
chmod +x ./examples/*.py
```
## Live Mode

Live mode is enabled by default.  You can type python commands into your
terminal and interact with qork if you prefer to do it directly.

## Getting Started

Qork has a zero-mode, inspired by pygame-zero,
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
def update(dt):
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

### Names and Tags

(not yet implemented)

An object can have any named tag and you can filter objects with these tags.

```
obj = add('Name')
obj.tag('tag')

find('Name') # -> [obj]

find('#tag') # -> [obj]

find_one('#tag') # -> obj
```

You can also limit your search to a certain node:

```
node.find('#tag')
```

### States

...

### Events

Create and trigger events with callbacks

```
player.heal = player.event('heal')
player.heal += lambda hp: print('Healed ', hp)

player.heal(10)
```

Event callbacks using connect() are scoped to the lifetime of the returned connection

```
my_heal_event = player.heal.connect(lambda: wrapper.func())

del my_heal_event # goodbye
```

## Camera

In zero mode, the camera is a global called `camera`.

```
camera.position = (0,0,5) # back up the camera by 5 units

camera.fov = util.degrees(80) # change field of view (usually in turns, but we use degrees here)

camera.ortho = True
```

## Input

...

## Resource Cache

Resources are automatically cached for later reuse and reference counted.

## Advanced (Reactive Classes)

### Signal

...

### Reactive

...

### Lazy

...


## Composites

Qork supports the composite design pattern.  That means, you can treat containers of
objects as a single object, where every function
you call on those trigger the objects with that function.

These objects may of may not be attached with each other in the scenegraph.

```py
ten_objects = add(10) # make 10 objects
ten_objects.scale(2) # scale all of these objects by 2

for obj in ten_objects: # loop through them like a list
    print(obj)
```

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
type: 'Sprite'
size: [ 16, 16 ]
tile_size: [ 16, 16 ]
origin: [ 0.5, 0.75 ]
mask: [ 0.25, 0.5, 0.75, 1.0 ]
states: ['life', 'direction', 'stance']
animation_speed: 10.0
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
player.state['stance'] = 'walk'
```

## Scripts

More to come soon!  Work in progress!


