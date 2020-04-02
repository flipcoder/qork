#!/usr/bin/env python
import glm
import math
from .reactive import *
from .signal import *
from glm import vec2, vec3, vec4, mat4
from .defs import *
from .util import *
from .easy import qork_app
import weakref


class MockApp:
    def __init__(self):
        self.cache = None
        self.ctx = None


class Node:
    def __init__(self, *args, **kwargs):
        if args:
            arg0 = args[0]

            # sanity check -- make sure count was popped by create()/add()
            assert not isinstance(arg0, int)

            if arg0 is None or isinstance(arg0, str):  # None or filename
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
            self.name = kwargs.get("name") or self.__class__.__name__
        try:
            # filename injected before super() call or resolved?
            self.fn
        except AttributeError:
            self.fn = filename_from_args(args, kwargs)

        self.cache = app.cache
        self.ctx = app.ctx
        self.args = args
        self.kwargs = kwargs

        self.children = Container()
        self.components = Container()

        # if not hasattr(app,'cache'):
        #     self.cache = app.cache
        # if not hasattr(app,'ctx'):
        #     self.cache = app.ctx

        self.visible = True
        self.num = kwargs.pop("num", 0)
        self.self_visible = True
        self._parent = None
        self.is_root = False
        self.transform = mat4(1.0)
        # self.detach_me = []
        self.deinited = False

        self.on_deinit = Signal()
        self.on_detach = Signal()
        self.on_event = Signal()
        self.on_state = Signal()
        self.on_update = Signal()
        self.on_pend = Signal()

        self.overlap = Signal()
        self.old_pos = vec3(0)

        self._vel = vec3(0)
        self._accel = vec3(0)
        self._states = {}
        self.destroyed = False
        self.connections = Connections()
        # self.scripts = Signal()

        self.world_transform = Lazy(self.calculate_world_matrix, [self.on_pend])

        # self.local_box = Lazy(self.local_box, [self.on_pend])
        self._local_box = Reactive()
        self._world_box = Lazy(
            self.calculate_world_box, [self.on_pend, self._local_box]
        )

    def __iter__(self, recursive=False, onlyself=False):
        yield self
        if not onlyself:
            for ch in self.children:
                yield from ch.__iter__(recursive, onlyself=not recursive)

    def each(self, func, recursive=False, onlyself=False):
        for n in self.__iter__(recursive, onlyself):
            func(n)

    def calculate_world_box(self):
        lbox = self._local_box
        r = []
        if not lbox:
            return None
        r = [vec3(), vec3()]  # min, max
        for i, v in enumerate(lbox):  # min, max
            r[i] = (self.matrix(WORLD) * vec4(v, 1)).xyz
        return r

    def calculate_world_matrix(self):
        if self.parent:
            return self.parent.matrix(WORLD) * self.transform
        else:
            return self.transform

    @property
    def world_box(self):
        return self._world_box()

    @world_box.setter
    def world_box(self, b):
        assert False  # not yet impl

    @property
    def local_box(self, b):
        return self._local_box()

    @local_box.setter
    def local_box(self, b):
        self._local_box = b  # !

    def set_local_box(self, b):
        self._local_box = b  # !

    # @box.setter
    # def box(self, b):
    #     self._box.set(b)

    # @property
    # def min(self):
    #     return self._local_box()[0]

    # @property
    # def max(self):
    #     return self._local_box()[1]

    # @min.setter
    # def min(self):
    #     self._local_box[0] = s

    # @max.setter
    # def max(self, s):
    #     self.box[1] = s

    def connect(self, sig, weak=True):  # for Lazy and Reactive
        return self.on_pend.connect(sig, weak)

    def __iadd__(self, con):
        self.connections += con

    def __isub__(self, con):
        self.connections -= con

    def __enter__(self):
        return self.children.__enter__()

    def __exit__(self, typ, val, tb):
        return self.children.__exit__(typ, val, tb)

    def __getitem__(self, name):
        # warning: idx may change across frames
        if isinstance(name, int):  # name is idx
            return self.children[name]
        with self.children:
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
        self.transform = glm.rotate(self.transform, turns * 2.0 * math.pi, axis)
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
        return self._vel

    @velocity.setter
    def velocity(self, *v):
        if v is None:
            self._vel = None
            return None
        self._vel = to_vec3(*v)
        return self._vel

    @property
    def vel(self):
        return self._vel

    @vel.setter
    def vel(self, *v):
        self.velocity = v

    def accelerate(self, *a):
        self._accel += to_vec3(*a)
        return self._accel

    @property
    def acceleration(self):
        return self._accel

    @acceleration.setter
    def accceleration(self, a):
        if a is None:
            return self._accel
        self._accel = a

    @property
    def accel(self):
        return self._accel

    @accel.setter
    def accel(self, a):
        if a is None:
            self._accel = vec3(0)
            return
        self._accel = a

    def reset_orientation(self, v=None, space=LOCAL):
        for i in range(3):
            self.transform[i] = vec4(AXIS[i], 0)

    def reset_scale(self):
        for i in range(3):
            self.transform[i] = vec4(glm.normalize(self.transform[i].xyz))

    def rescale(self, v=None, space=LOCAL):
        self.reset_scale()
        self.scale(v, space)

    def scale(self, v=None, space=LOCAL):
        if v is None:
            assert False  #
        if type(v) in (int, float):
            v = vec3(float(v))
        if space == LOCAL:
            self.transform *= glm.scale(mat4(1.0), v)
        elif space == PARENT:
            self.transform = glm.scale(mat4(1.0), v) * self.transform
        else:
            assert False  # not impl
        self.world_transform.pend()

    def _position(self, v=None, space=None):
        if type(v) == int and space is None:
            space = v
            v = None
        if space is None:
            space = PARENT
        if v is None:  # get
            if space == PARENT:
                return self.world_transform()[3].xyz
            elif space == WORLD:
                return vec3(self.world_transform()[3].xyz)
            assert False
        assert space == PARENT  # not impl
        self.transform[3] = vec4(v, 1.0)  # set
        self.pend()
        return v

    @property
    def x(self):
        return self.position.x

    @x.setter
    def x(self, v):
        p = self.position
        self.position = vec3(v, p.y, p.z)

    @property
    def y(self):
        return self.position.y

    @y.setter
    def y(self, v):
        p = self.position
        self.position = vec3(p.x, v, p.z)

    @property
    def z(self):
        return self.position.y

    @z.setter
    def z(self, v):
        p = self.position
        self.position = vec3(p.x, p.y, v)

    @property
    def vx(self):
        return self.velocity.x

    @vx.setter
    def vx(self, v):
        p = self.velocity
        self.velocity = vec3(v, p.y, p.z)

    @property
    def vy(self):
        return self.velocity.y

    @vy.setter
    def vy(self, v):
        p = self.velocity
        self.velocity = vec3(p.x, v, p.z)

    @property
    def vz(self):
        return self.velocity.y

    @vz.setter
    def vz(self, v):
        p = self.velocity
        self.velocity = vec3(p.x, p.y, v)

    @property
    def ax(self):
        return self.acceleration.x

    @vx.setter
    def ax(self, v):
        p = self.acceleration
        self.acceleration = vec3(v, p.y, p.z)

    @property
    def ay(self):
        return self.acceleration.y

    @vy.setter
    def ay(self, v):
        p = self.acceleration
        self.acceleration = vec3(p.x, v, p.z)

    @property
    def az(self):
        return self.acceleration.y

    @vz.setter
    def az(self, v):
        p = self.acceleration
        self.acceleration = vec3(p.x, p.y, v)

    @property
    def position(self):
        return self._position()

    @position.setter
    def position(self, *p):
        self.old_pos = self.position
        self._position(to_vec3(*p))

    @property
    def world_position(self):
        return self._position(WORLD)

    @property
    def pos(self, *p):
        return self._position()

    @pos.setter
    def pos(self, *args):
        self._position(to_vec3(*args))

    @property
    def world_pos(self):
        return self._position(WORLD)

    def move(self, *v):
        self.transform[3] += vec4(to_vec3(*v), 0.0)
        self.pend()

    def pend(self):
        self.on_pend()
        with self.children:
            for ch in self.children:
                ch.pend()

    @property
    def parent(self):
        if not self._parent:
            return None
        p = self._parent()
        if not p:
            self._parent = None
            return None
        return p

    @parent.setter
    def parent(self, p):
        self._parent = weakref.ref(p)

    def attach(self, *args, **kwargs):
        if args and isinstance(args[0], int):
            assert False  # not yet impl here
        if args and isinstance(args[0], Node):
            node = args[0]
            assert not node.parent
            self.children += node
            node._parent = weakref.ref(self)
            self.pend()
            return node
        else:
            return self.attach(self.app.create(*args, **kwargs))

    def add(self, *args, **kwargs):  # alias for attach
        return self.attach(*args, **kwargs)

    # Implementing this will enable script on node
    # def script(self, dt):
    #     pass

    def update(self, dt):
        for component in self.components:
            component.update(self, dt)

        if self._accel:
            self.velocity += self._accel * dt
        if self._vel:
            self.position += self._vel * dt

        self.on_update(self, dt)

        assert self.children._blocked == 0
        with self.children:
            for ch in self.children:
                ch.update(dt)

        # if self.detach_me:
        #     detach_me = self.detach_me
        #     self.children = list(filter(lambda x: x not in detach_me, self.children)) #     self.detach_me = []
        #     for node in detach_me:
        #         node.on_detach(node)

    def destroy(self):
        if not self.destroyed:
            self.destroyed = True

    # def safe_detach(self, func=None):
    #     if self.parent:
    #         self.parent.detach_me.append(self)
    #         if func:
    #             self.on_detach.connect(func, weak=False)

    def detach(self, node=None):
        if node is None:  # detach self
            if self.parent:
                self.parent.children -= node
                assert node not in self.parent.children
            # self.parent.children = list(
            #     filter(lambda x: x != self, self.parent.children)
            # )
            self.on_detach()
            self._parent = None
            self.pend()
        else:
            assert node._parent == self
            node.detach()

    # def safe_remove(self, node=None):
    #     return self.safe_detach(node)

    def remove(self, node=None):
        return self.detach(node)

    def render(self):
        if self.visible:
            for component in self.components:
                component.render(self)
            for ch in self.children:
                ch.render()

    def clean(self):  # called by Core as an explicit destructor
        if not self.deinited:
            self.on_deinit()
            for ch in self.children:
                ch.deinit()
            self.deinited = True
