#!/usr/bin/env python
import glm
import math
from .reactive import *
from glm import vec2, vec3, vec4, mat4
from .defs import *
from .util import *
from .zero import qork_app

class MockApp:
    def __init__(self):
        self.cache = None
        self.ctx = None

class Node:
    def __init__(self, *args, **kwargs):
        if args:
            arg0 = args[0]
            if arg0 is None or isinstance(arg0, str): # None or filename
                self.app = app = qork_app()
                if not app:
                    self.app = app = MockApp()
            else:
                app = self.app = arg0
        else:
            self.app = app = qork_app()
            if not app:
                app = self.app = MockApp()
        
        try:
            self.name
        except AttributeError:
            self.name = kwargs.get('name') or self.__class__.__name__
        try:
            # filename injected before super() call or resolved?
            self.fn
        except AttributeError:
            self.fn = filename_from_args(args, kwargs)
        
        self.cache = app.cache
        self.ctx = app.ctx
        self.args = args
        self.kwargs = kwargs
        # if not hasattr(app,'cache'):
        #     self.cache = app.cache
        # if not hasattr(app,'ctx'):
        #     self.cache = app.ctx
        self.visible = True
        self.self_visible = True
        self.children = []
        self.parent = None
        self.transform = mat4(1.0)
        self.components = []
        self.detach_me = []
        self.deinited = False
        self.on_deinit = Signal()
        self.on_detach = Signal()
        self.on_event = Signal()
        self.on_state = Signal()
        self.on_update = Signal()
        self._vel = None
        self._accel = None
        self.being_destroyed = False # scheduled to be destroyed?
        self.destroyed = False
        self.on_pend = Signal()
        self._states = {}
        
        def calculate_world_matrix():
            if self.parent:
                return self.parent.matrix(WORLD) * self.transform
            else:
                return self.transform
        
        self.world_transform = Lazy(calculate_world_matrix, [self.on_pend])
    
    def connect(self, sig): # for Lazy and Reactive
        return self.on_pend.connect(sig)
    
    def __getitem__(self, name):
        if isinstance(name, int):
            return self.children[name]
        for ch in self.children:
            if ch.name == name:
                return ch
        raise IndexError
    
    def state(self, category, value=DUMMY):
        # first arg is a list of states? set those instead
        if isinstance(category, dict):
            self._states = category
            for state, value in self._states.items():
                self.on_state(state, value)
            return category
        # otherwise, the args mean what they say
        if s is DUMMY:
            return self._states[category]
        elif s is None:
            del self._states[category]
        if isinstance(str, category):
            self._states[category] = value
            self.on_state(value)
        else:
            assert False
        return s
    def states(self, category, value=DUMMY):
        return self.state(category, value)
    def event(self, *args, **kwargs):
        self.on_event(*args, **kwargs)
    # def __call__(self, *args, **kwargs):
    #     self.event(*args, **kwargs)
    def matrix(self, space=PARENT):
        assert space != LOCAL
        if space == PARENT:
            return self.transform
        return self.world_transform()
    def rotate(self, turns, axis=Z):
        self.transform = glm.rotate(
            self.transform, turns * 2.0 * math.pi, axis
        )
        self.pend()
    def __str__(self):
        return self.name

    def stop(self):
        was_moving = bool(self.vel or self.accel)
        self.vel = None
        self.accel = None
        return was_moving
        
    @property
    def velocity(self):
        return self._vel or vec3(0)
    
    @velocity.setter
    def velocity(self, *v):
        if v is None:
            self._vel = None
            return None
        self._vel = to_vec3(*v)
        return self._vel or vec3(0)

    @property
    def vel(self):
        return self.velocity()
    
    @vel.setter
    def vel(self, *v):
        self.velocity = v
        return self.velocity
    
    def accelerate(self, *a):
        self._accel += to_vec3(*a)
        return self._accel
    
    @property
    def acceleration(self):
        return self._accel or vec3(0)
    
    @acceleration.setter
    def accceleration(self, a):
        if a is None:
            return self._accel or vec3(0)
        self._accel = a

    @property
    def accel(self):
        return self._accel or vec3(0)
    
    @accel.setter
    def accel(self, a):
        if a is None:
            return self._accel or vec3(0)
        self._accel = a

    
    def scale(self, v=None, space=LOCAL):
        if v is None:
            assert False #
        if type(v) == int or type(v) == float:
            v = vec3(float(v))
        if space == LOCAL:
            self.transform *= glm.scale(mat4(1.0), v)
        elif space == PARENT:
            self.transform = glm.scale(mat4(1.0), v) * self.transform
        else:
            assert False # not impl
        self.world_transform.pend()
    
    def _position(self, v=None, space=None):
        if type(v) == int and space is None:
            space = v
            v = None
        if space is None:
            space = PARENT
        if v is None: # get
            if space == PARENT:
                return self.world_transform()[3].xyz
            elif space == WORLD:
                return vec3(self.world_transform()[3].xyz)
            assert False
        assert space == PARENT # not impl
        self.transform[3] = vec4(v, 1.0) # set
        self.pend()
        return v
    
    @property
    def position(self):
        return self._position()
    
    @position.setter
    def position(self, *p):
        return self._position(to_vec3(*p))
    @property
    def world_position(self):
        return self._position(WORLD)
    
    @property
    def pos(self, *p):
        return self._position()
    @pos.setter
    def pos(self, *args):
        return self._position(to_vec3(*args))
    @property
    def world_pos(self):
        return self._position(WORLD)
    
    def move(self, *v):
        self.transform[3] += vec4(to_vec3(*v), 0.0)
        self.pend()
    
    def pend(self):
        self.on_pend()
        for ch in self.children:
            ch.pend()
    def attach(self, *args, **kwargs):
        if args and isinstance(args[0], Node):
            node = args[0]
            assert not node.parent
            self.children.append(node)
            node.parent = self
            self.pend()
            return node
        else:
            return self.attach(self.app.Entity(*args, **kwargs))
    def add(self, *args, **kwargs): # alias for attach
        return self.attach(*args, **kwargs)
    def update(self, dt):
        for component in self.components:
            self.components.update(self, dt)
 
        new_vel = None
        if self._accel is not None:
            new_vel = self._vel
            self._vel += self._accel / 2.0 * dt
            new_vel += self._accel * dt
        if self._vel is not None: # velocity not zero
            self.move(self._vel * dt)
        if new_vel is not None: # accelerated
            self._vel = new_vel
        
        self.on_update(self, dt)

        for ch in self.children:
            ch.update(dt)
        if self.detach_me:
            detach_me = self.detach_me
            self.children = list(filter(
                lambda x: x not in detach_me, self.children
            ))
            self.detach_me = []
            for node in detach_me:
                node.on_detach(node)
        
    def destroy(self):
        if not self.being_destroyed:
            self.detach()
            self.app.cleanup_list.append(self) # schedule Core to cal clean()
            self.destroyed = True
    def safe_detach(self, func=None):
        if self.parent:
            self.parent.detach_me.append(self)
            if func:
                self.on_detach.connect(func)
    def detach(self, node=None):
        if node is None: # detach self
            self.parent.children = list(filter(
                lambda x: x != self, self.parent.children
            ))
            self.on_detach()
            self.parent = None
            self.pend()
        else:
            assert node.parent == self
            node.detach()
    def safe_remove(self, node=None):
        return self.safe_detach(node)
    def remove(self, node=None):
        return self.detach(node)
    def render(self):
        if self.visible:
            for component in self.components:
                self.components.render(self)
            for ch in self.children:
                ch.render()
    def clean(self): # called by Core as an explicit destructor
        if not self.deinited:
            self.on_deinit()
            for ch in self.children:
                ch.deinit()
            self.deinited = True

