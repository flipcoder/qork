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

## Usage

Classes:
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

