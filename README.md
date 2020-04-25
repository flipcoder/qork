# qork

Qork is a zero-boilerplate 3D+2D python OpenGL framework

This means an empty file is a valid blank window program.

Getting an image on the screen and moving around requires only one line of code:

```
add('hello_world.png', vel=X)
```

This will spawn an image with 1 unit/sec velocity to the right (X dir)

This will also start the live-coding console w/ autocomplete, where you can
add code and play around with qork.

It is VERY NEW, so some things are only partially implemented, and not
all examples and resources are done and included.  But feel free to look around!

If you're familiar with gamedev, dive into the example folder or source!

## Details

- Matrix Transforms: Position, Rotation, Scale
- Position, Velocity, Acceleration
- Hierarchical Scenegraph similar to Unity
- Live-coding async console using ptpython (prompt-toolkit)
- Resource Management
- Object Events
- State Machines
- Sprite Animation (not yet done)
- Time-based callback scheduling
- Reactive Types (signals, reactive variables, observer-based lazy evaluation)
- Reactive Metadata (Easily add reactive properties to your states and nodes)
- Optional Minimal Function Names for Code-Golfing

## Integration

- pyGLM: matrix and vector math
- Cairo (pyCairo): canvas drawing
- OpenAL (pyOpenAL): 3d sound (SOON)
- bullet (SOON): physics
- pytweening (SOON): easing functions

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

Firstly, you'll want to run your program through qork instead of python.

You can use a shebang line if you want to execute it directly
on Linux and Mac or rename it to a .qork file and associate
that with qork on windows. This is optional.

Here's the shebang line if you want it:

```
#!/usr/bin/env qork
```

Let's load a player image and display it on the screen:

```
player = add('player.png')
```

Let's set the camera position:
camera.pos = (1,2,3)

Provide an x,y,z coordinate as a 2d or 3d tuple, or a vec2/vec3 object.

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
    player.pos += Y * 2 * dt
```

X, Y, and Z are vectors (1,0,0), (0,1,0) and (0,0,1).  These give us directions.

When you change position every frame instead of setting velocity,
remember to multiply it by t. This will allow for variable fps.

If you do not want variable fps, you can remove the dt and it will default
to 60fps.

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
node.pos = (0,0) # 2D

node.pos = vec2(0,0)
    
node.pos = (0,0,0) # 3D
    
node.pos = vec3(0,0,0)

node.move(1,2,3) # relative movement (changes position)

node.move(vec2(1,2))

node.move(vec3(1,2,3))

```

You can use pos or position if you prefer.

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

You can also change components individually, like this:

```
node.x = 1
node.y = 2
node.z = 2

# velocity:

node.vx = 1
node.vy = 2
node.vz = 3

# acceleration:

node.ax = 1
node.ay = 2
node.az = 2
```

### Attaching

Nodes can be attached to another, so they are moved along with the parent.

```
parent = add() # add parent to scene
child = parent.add() # add a new child to parent
```

Node positions are relative to their parents, so if you want to get
the real world position of a node, use `world_position`

```
print(child.world_position)

# or...

print(child.wpos)
```

### Angular Velocity

```
node.angular_velocity(1) # 1turn/s around Z axis

node.angular_velocity(1, Z) # or with axis
```

### Detaching

```
child.remove()

# or...

parent = remove(child)

# and to remove the parent

parent.remove()

# or...

remove(parent)
    
```

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
p = add('Player')
p.tag('red')

find('Player') # -> [p]

find('#red') # -> [p]

find_one('#red') # -> p

# or use a function....

p.find(lambda x: x.name=='Player')

```

You can also limit your search to a certain node:

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

### Camera

In zero mode, the camera is a global node called `camera`.

```
camera.position = (0,0,5) # back up the camera by 5 units

camera.fov = deg(80) # change field of view (usually in turns, but we use degrees here)

camera.ortho = True # turn on 2D mode

camera.mode = '3D' # same as setting ortho to False

```

## Input

- KEY: array containing all the keys (use autocomplete in the qork console to see them all)
- key(k): check if a key is pressed down
- key_pressed(k): check if a key was just pressed
- key_released(k): check if a key was just released
- keys(): a set containing all the pressed keys
- keys_pressed(): a set containing all the keys that were just pressed
- keys_released(): a set containing all the keys that were just pressed
- click(n): True if mouse button number `n` was just pressed
- unclick(n): True iif mouse button number `n` was just released
- hold_click(n): True iif mouse button `n` is being held
- mouse_buttons(): a set containing all the pressed mouse buttons
- mouse_buttons_pressed(): a set containing the mouse buttons that were just pressed
- mouse_buttons_released(): a set containing the mouse buttons that were just released
- mouse_pos(): get the current mouse position

```
def update(dt):
    if key(KEY.SPACE):
        shoot()
```

The following function implements "pong" controls:

```
def update(dt):
    paddle[0].vy = (key(KEY.W) - key(KEY.S)) * paddle_speed
    paddle[1].vy = (key(KEY.UP) - key(KEY.DOWN)) * paddle_speed
     
```

## Resources

Resources are automatically cached for later reuse and reference counted.

You can set the data_path two ways:

```
data_path('data')

data_paths(['.'], ['data'])
```

## Advanced (Reactive Classes)

### Signal

```
sig = Signal()
sig += lambda: print('hello ', end='')
sig += lambda: print('world')
sig() # hello world
```

### Slots

```
# Make a signal

sig = Signal()

# Connect some slots (Note this is different from the above Signal example)

hello += sig.connect(lambda: print('hello ', end=''))
world += sig.connect(lambda: print('world'))

sig() # hello world

# let's remove hello slot

hello.disconnect()

sig() # world

# here's another way to remove a slot

sig -= world

# or...

del world

# Node: The above `del` relies on the garbage collector, which is not fully reliable.

```

### Reactive

Reactive variables are paired with an on_change signal.

```
x = Reactive(1)

x += lambda x: print('x is now', x)

x(2)  # This is sets to 2 and will print: "x is now 2"

# Inc/Dec operators of non-callable values are forwarded to enclosed value:

x += 1 # "x is now 3"
```

### Lazy

Lazy values are functions that are called only when the value is needed

```

equation = Lazy(lambda: 2 * math.pi)
equation() # computed!
equation() # value is returned again, since it has already been computed

```

Lazy values can depend on other lazy or reactive values:

```
x = Reactive(2)
y = Reactive(3)
equation = Lazy(lambda: x() + y(), [x, y])

equation() # 5 (computed and cached)
equation() # 5 (return cached value)

x(1) # invalidates the equation

equation() # 4 (recomputes since it was invalidated)
```

## Composites

This feature is not fully implemented.

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

## Spritesheets

This is not yet fully implemented.

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

## "Code-Golfing"

Qorks includes some code-golfing functions and variables.

Some of these are not yet implemented, but this is what is planned so far:

-globals:
    - A: add
    - R: remove
    
    - P: play wav sound or stream music
    - Q: stop all sound or music
    
    - S: sin(tau * X)
    - C: cos(tau * X) if called, otherwise Camera
    - T: tan(tau * X)
    
    - R: rotate
    - X: scale
    - P: translate/reposition
    
    - W: world/scene

-node properties and methods

    - p: pos (or x, y, z)
    - v: vel (or vx, vy, vz)
    - a: accel (or ax, ay, az)
    
    - o: orientation
    - h: heading

    - s: scale (relative)
    - S: set scale (use S=2 to scale 2)
    - ss: scale space
    
    - ps: pos space
    - vs: vel space
    - as: accel space
    
    - rp: relative pos (or rx, ry, rz)
    
    - wp: world pos (or wx, wy, wz)
    
    - ra: rotation axis (or rax, ray, raz)
    - rs: rotation space
    - r: rotate
    
    - ro: reset orientation
    - rp: reset pos
    - rs: reset scale
    
    - O: omega (angular velocity)
    - W: omega axis

## Scripting

Qork includes an async scripting system using generators:

```
def script(ctx):
    while True:
        # do this every second
        yield ctx.sleep(1) # wait 1 second
```

Calling a function 'script' in a qorkscript starts it with the program.

## LICENSE

MIT License. See LICENSE file for details.

Copyright (c) 2020 Grady O'Connell

