# qork

Qork is a zero-boilerplate 3D+2D python OpenGL framework.

This means an empty file is a valid blank window program.

Getting an image on the screen and moving around requires only one line of code:

```
add('hello_world.png', pos=-X, vel=X, spin=1)
```

This will spawn an image on the left hand side of the screen,
moving 1 unit/sec to the right (X dir), spinning 1turn/sec.

This will also start the live-coding console w/ autocomplete, where you can
add code and play around with qork.

This framework is VERY NEW, so some things are only partially implemented, and not
all examples and resources are done and included.  But feel free to look around!

If you're familiar with gamedev, dive into the example folder or source!

## Details

- Matrix Transforms: Position, Rotation, Scale
- Position, Velocity, Acceleration
- Hierarchical Scenegraph, similar to modern game engines
- Input Handling
- Live-coding async console using ptpython (prompt-toolkit)
- Resource Management
- Object Events
- State Management
- Sprite Animation
- Time-based callback scheduling
- Reactive Types (signals, reactive variables, observer-based lazy evaluation)
- Reactive Metadata (Easily add reactive properties to your states and nodes)
- Optional Minimal Function Names for Code-Golfing

## Integration

- pyGLM: matrix and vector math
- Cairo (pyCairo): canvas drawing
- pyTMX: tilemaps
- OpenAL (pyOpenAL): 3d sound (SOON)
- bullet (SOON): physics

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

The below velocity code will start node moving at 1unit/sec in the positive X

```
node.velocity = X
```

You can also change acceleration

```
node.acceleration = Z # set acceleration in positive Z direction

node.acceleration = (1,2) # in 2d

node.acceleration = (1,2,3) # in 3d

node.stop() # stops velocity and acceleration
```

You can use `vel` and `accel` if you prefer shorter names.

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

Like most game engines, nodes in the scene can be attached to each other so
that child nodes are connected to their parents, inheriting the position and
orientation changes of the parent while keeping their own relative positioning and
orientation.

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
node.spin(1) # 1 turn per sec around Z axis

node.spin(1, Y) # or with axis
```

You can change the default for all nodes:

```
Node.ROTATION_AXIS = Y
```

### Detaching

```
child.remove()

# or...

parent.remove(child)

# and to remove the parent

parent.remove()

# or...

remove(parent)
    
```

### Rotation/Scaling

Qork angles are based on **turns**. Rotating .5 is half a turn.

```
node.rotate(.25) # rotate quarter turn in 2D

node.rotate(.5, Y) # rotate half turn in 3D around Y axis
```

The second parameter to rotate can take any vector to rotate around.

### Names and Tags

An object can have any named tag and you can filter objects with these tags.

```
p = add('Player')
p.tag('red')

find('Player') # -> [p]

find('#red') # -> [p]

find_one('#red') # -> p

# or use a function....

find(lambda obj: obj.name=='Player') # -> p

```

You can also limit your search to a certain node:

### Node States

Any node can have a state machine if you need it.

```
# set up a callback
player.on_stage_change += lambda state, stance: print(state, "is now", stance)

# trigger!
player.state["stance"] = "attack"  # prints "stance is now attack"
````

These states can be used to automatically trigger an associated spritesheet animation.
We'll get into that later!

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

### Node Groups

This feature is not fully implemented.

Qork supports the composite design pattern for Nodes.  That means, you can treat groups of
objects as a single object, where every function
you call on those trigger the objects with that function.

This is different than just attaching nodes to a common parent, which is
probably what you want if you only want nodes to move or reorient together.

The nodes in a group may not be attached with each other in the scenegraph.

```py
ten_objects = add(10) # make 10 objects
ten_objects.scale(2) # scale all of these objects by 2

for obj in ten_objects: # loop through them like a list
    print(obj)
```

Node grouping is ideal for spawning an arbitrary number of similar objects
that you need to loop through.  When a group goes out of scope,
the attached nodes remain attached.

### Camera

In zero mode, the camera is a global node called `camera`.

```
camera.position = (0,0,5) # back up the camera by 5 units

camera.fov = deg(80) # change field of view (usually in turns, but we use degrees here)

camera.ortho = True # turn on 2D mode

camera.mode = '3D' # same as setting ortho to False

```

If you change game states, you get a new default camera and scene for that state.
You don't have to use this camera as the default.  You can create your own camera
and set it to be the default.

```
newCamera = add(Camera(default=True))
```

This will assoiate the camera with the current game state or, if you have no states,
the app itself.

## Input

- KEY: array containing all the keys (use autocomplete in the qork console to see them all)
- key(k): check if a key is pressed down
- key_pressed(k): check if a key was just pressed
- key_released(k): check if a key was just released
- keys(): a set containing all the pressed keys
- keys_pressed(): a set containing all the keys that were just pressed
- keys_released(): a set containing all the keys that were just pressed
- click(n): True if mouse button number `n` was just pressed
- unclick(n): True if mouse button number `n` was just released
- hold_click(n): True if mouse button `n` is being held
- mouse_buttons(): a set containing all the pressed mouse buttons
- mouse_buttons_pressed(): a set containing the mouse buttons that were just pressed
- mouse_buttons_released(): a set containing the mouse buttons that were just released
- mouse_pos(): get the current mouse position

```
def update(dt):
    if key(KEY.SPACE):
        shoot()
```

The following function implements "pong" controls for two players:

```
def update(dt):
    paddle[0].vy = (key(KEY.W) - key(KEY.S)) * paddle_speed
    paddle[1].vy = (key(KEY.UP) - key(KEY.DOWN)) * paddle_speed
     
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

```
player = add('player.cson')
player.state['stance'] = 'walk'
```

## Audio

```
sound = add('sound.wav') # Add a sound (does not autoplay)
sound.play() # play a sound
sound.play(once=True) # play a sound once, but keep it attached
sound.play(temp=True) # temporary sound, detach when done playing

sound.on_done += lambda: print('done') # callback when sound it done playing

play('test.wav') # play sound once and remove when done (attached to camera)
add('test.wav', temp=True).play() # same as above
add('test.wav').play(temp=True) # same as above

cache('test.wav') # preload a sound

sound = create('test.wav') # create a sound node to attach later
add(sound).play() # attach the precreated sound node and play it

sound.stop() # stop sound, but keep it attached
sound.remove() # stop sound and remove it from scene

play('music.ogg') # playing music is the same
```

3D positioning of sound is not yet implemented.

## Canvas

Qork contains a canvas class that can be used to draw text, shapes,
and gradients using a library called Cairo.

The default qork boilerplate contains two canvases: The background (called "backdrop"),
and the foreground canvas, simply called "canvas".  The background canvas always
draws below objects, while the main foreground canvas draws on top.

The qork canvas works similar to vector graphics and relies on pycairo.
Qork's canvas saves all the operations you do to a canvas and redraws them
whenever something changed since the last render.

It does this so that individual draw operations can be changed dynamically,
keeping the canvas elements individually accessible.  Let's touch more on this later.

### Text

To draw text to the screen, we have the canvas draw function:

```
def text(self, s, color, pos, flags, shadow=None)
```

It is used like this:

```
canvas.text('Hello world!', 'green')
```

...

### Gradients

This clears the backdrop to a 3-color gradient:

```
backdrop.gradient("lightblue", "blue", "black")
```

You can also add "stops", which are values from 0 to 1, which specify
where the color will fall.  Stops are automatically calculated if they
are not provided, and they should be called in order.

To add stop values, instead of providing just the color, provide a tuple per step:

```
backdrop.gradient(
    (0.0, 'red'),
    (0.1, 'orange'),
    (0.3, 'green'),
    (1.0, 'white')
)
```

The colors you specify can eiher be string names or types of class Color,
which are 4d vectors of RGBA colors.

```
backdrop.gradient(Color(1,0,0), Color(0,1,0), Color(.5,.5,.5))
```

It should be noted that clearing to a gradient ADDS a clear to the canvas draw routine.
it doesn't remove past gradients.  So if you keep calling this function, the gradients
will be combined every time you need to redraw.

So if you wish to reset the primary gradient, pass `clear=True` into the gradient function:

```
backdrop.gradient('white', 'black', clear=True)
```

or simply clear beforehand, which removes all draw steps:

```
backdrop.clear()
backdrop.gradient('white', 'black')
```

Or if you want to clear to a solid color:

```
backdrop.clear('black')
```

To set gradient region:

```
backdrop.gradient('red', 'green', region=[0,0,0,100])
```

To do a radial gradient, provide a tuple of the (x,y,rad) of the 
2 circles, as you would in pycairo.

We'll use half the screen size and a radius of 10 to 1000:

```
r = (
    (*Q.size/2, 10),
    (*Q.size/2, 1000)
)
backdrop.gradient('white', 'black', radial=r)
```

### Shapes (and pycairo access)

Each cairo operation inserts a draw step that only gets called
when the canvas needs to be redrawn.  You can remove these draw steps
by disconnecting the connection that is returned by the pycairo function
that is called, or you may clear the entire canvas to remove everything.

This will draw a centered red rectangle of half the screen size

```
canvas.rectangle(*canvas.res/4, *canvas.res/2)
canvas.source = 'red'
canvas.fill()
```

Qork's canvas methods contain mostly mirrors of pycairo methods, so you
can use pycairo's api, with the exception of methods with the same name
as Node methods, in which case the cairo method will be prefixed with "canvas_"
to distinguish it from operations on the Canvas node itself.  An example
of this is `translate`, which has been renamed to `canvas_translate` as not
to confuse translation of the Canvas node itself.  Keep this in mind if you
ever have issues with using cairo methods!

### Custom Canvas

If you wish to make a custom canvas, simply add one as a node:

```
mycanvas = add(Canvas())
```

Canvases are quad meshes which allow you to draw onto the texture.  They can be
manipulated just like any other Node in qork.  You can use them to easily
create procedural game textures.

Canvases which are declared separately are rendered in the same layer as other
objects since they are not restricted to the background or foreground like the two
default canvases.

### Batching

Certain operations on a canvas can be batched together and enabled, disabled,
or disconnected entirely.

Here is an example:

```
red_square = canvas.batch('red')
with red_square:
    canvas.source = 'red'
    canvas.rectangle(*canvas.res/2, *canvas.res/2)
    canvas.fill()
```

This puts a red square onto the canvas's draw queue.  It can then be removed
from the canvas without effecting the rest of the canvas draw operations
like this:

```
red_square.disconnect()
```

Since this is the only thing on the canvas, other than the default clear
operation, the canvas will be blank after disconnecting this.  But if you
had other canvas operations, the canvas would be redrawn in the order of
your previous draw calls, but with the removal of the red square batch.

You can also temporarily disable a batch and re-enable it when you wish:

```
red_square.disable()

# later...

red_square.enable()
```

## Game States

Game states are used to keep your game separated into different parts.
Your game might need a menu, a score screen, and the game itself.

If you want a separate scene and camera for these states, create separate
states by inheriting from the State base class:

```
class Game(State):
    def __init__(self, *args, **kwargs):
        super().__init__(self)
    def update(self, dt):
        super().update(dt)

Q.states.change(Game) # make GameState the current state
```

When you're using states, the global camera will no longer be used.
Instead, use the state's camera (self.camera if you're inside the State class).

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

## Scripting

Qork includes an async scripting system using generators:

```
def script(ctx):
    while True:
        # do this every second
        yield 1 # wait 1 second
```

Delay a script for a specific length of time in seconds:


```
yield 1.0
```

Delay a script until a condition is true

```
yield lambda: ctx.key(KEY.SPACE)
```

(Advanced) You can also yield event slots:

```
yield when.once(1, script.resume)
```

Calling a function 'script' in a qorkscript starts it with the program.

### Node Scripting

All nodes are scriptable, and you can attach a script to them using
the `+=` operator, and remove it using the `-=` operator.

```
def my_script(ctx):
    while True:
        # TODO: do this every second
        yield 1
    
node = Node()
node += my_script
```

The script will start when attached and continue until it reaches the end
or is detached.

## LICENSE

MIT License. See LICENSE file for details.

Copyright (c) 2020 Grady O'Connell

