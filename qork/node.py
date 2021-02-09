#!/usr/bin/env python
import glm
import math
import pathlib
import pprint
from .box import *
from .reactive import *
from .signal import *
from .when import *
from glm import vec2, vec3, vec4, mat4
from .defs import *
from .minimal import MinimalCore
from .util import *
from .easy import qork_app
from itertools import chain
import weakref
from .script import Script
from .scriptable import Scriptable
from typing import Optional
from collections import defaultdict
from .states import StateMachine


class Events(defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(Signal)

    def __call__(self, name, *args, **kwargs):
        return self[name]


class Node(Scriptable):
    ROTATION_AXIS = -Z
    collision_handler = False

    def __init__(self, *args, **kwargs):
        if args:
            arg0 = args[0]

            if isinstance(arg0, MinimalCore):
                app = self.app = arg0
            else:
                app = self.app = qork_app()

            # # sanity check -- make sure count was popped by create()/add()
            # assert not isinstance(arg0, int)

            # if arg0 is None or isinstance(arg0, str):  # None or filename
            #     self.app = app = qork_app()
            #     if not app:
            #         self.app = app = MinimalCore()
            # elif isinstance(arg0, (tuple,float,vec3,vec2)):
            #     return qork_app()
            # else:
            #     app = self.app = arg0
        else:
            app = self.app = qork_app()

        if not app:
            app = self.app = MinimalCore()

        assert self.app

        try:
            # filename injected before super() call or resolved?
            self.fn
        except AttributeError:
            # find the resource's true path
            self.fn = filename_from_args(args, kwargs)
            # if '.' not in self.fn:
            #     self.connections += self.watch_resource(self.fn, self.modify)

        if self.fn:
            self.ext = pathlib.Path(self.fn).suffix
        else:
            self.ext = ""

        if self.ext:
            # print(os.path.dirname(self.app.script_path))
            script_dir = os.path.dirname(self.app.script_path)
            pth = os.path.join(script_dir, self.fn)
            if os.path.exists(pth):
                self.path = pth
            else:
                self.path = None
                for dp in self.app._data_paths:
                    pth = os.path.join(os.path.join(script_dir, dp, self.fn))
                    if os.path.exists(pth):
                        self.path = pth
                        break

        num = self.num = kwargs.pop("num", None)
        try:
            self.name
        except AttributeError:
            if num is not None:
                self.name = kwargs.pop("name", None) or self.fn or str(self.num)
            else:
                self.name = (
                    kwargs.pop("name", None) or self.fn or self.__class__.__name__
                )

        self._inherit_transform = Reactive(True)
        self._root: Optional[weakref.ref] = None
        self.cache = self.app.cache
        self.ctx = self.app.ctx

        # for reloading or copying?
        self.args = args
        self.kwargs = kwargs

        self.tags = set()

        self.frozen = False
        self.frozen_children = False

        self._spin = kwargs.pop("spin", None)
        self.spin_axis = self.ROTATION_AXIS
        self.spin_space = PARENT

        self._size = kwargs.pop("size", None)
        self.is_root = kwargs.pop("root", False)

        self.children = Container()
        # self.components = Container()

        # if not hasattr(app,'cache'):
        #     self.cache = app.cache
        # if not hasattr(app,'ctx'):
        #     self.cache = app.ctx

        self.invisible = 0
        # self.self_visible = True
        self.children_visible = True
        self._parent = None
        self._partitioner = None

        # transform matrix, triggers inherited children on change and any listeners
        self._matrix = Reactive(mat4(1.0), [self])

        # set this manually to override the world matrix when rendering
        # self._matrix_func = None

        # self.detach_me = []
        # self.deinited = False

        self.when = When()
        # self.on_detach_child = Signal()  # child arg
        # self.on_detach_self = Signal()  # parent arg

        # Signals will be created when they're accessed
        self._on_deinit = None
        self._event = None
        self._on_update = None
        self._on_add = None
        self._on_remove = None

        # self.on_state = Signal()
        self.on_pend = Signal()

        # self.overlap = Signal()
        self.old_pos = vec3(0)

        self._vel = None
        # self.vel_space = Space.PARENT
        self._accel = None
        # self.accel_space = Space.PARENT
        # self._states = {}
        self.destroyed = False

        self.connections = Connections()

        self.state = StateMachine(self)
        self.on_state_change = self.state.on_state_change

        self._setup_world_matrix()

        # self.local_box = Lazy(self.local_box, [self.on_pend])
        self._local_box = Reactive()
        self._world_box = Lazy(
            self._calculate_world_box,
            [self._matrix, self._local_box, self._inherit_transform],
        )

        # allow connections through .on_pend

        pos = (
            kwargs.pop("position", None)
            or kwargs.pop("pos", None)
            or kwargs.pop("p", None)
        )
        vel = (
            kwargs.pop("velocity", None)
            or kwargs.pop("vel", None)
            or kwargs.pop("v", None)
        )
        rot = (
            # kwargs.pop("rotation", None)
            kwargs.pop("rot", None)
            or kwargs.pop("r", None)
        )
        scale = kwargs.pop("scale", None) or kwargs.pop("s", None)

        if num is not None:
            # allow `add(5, pos=lambda n: (n*10, 0, 0))
            n = self.num
            if callable(pos):
                pos = to_vec3(pos(n))
            if callable(vel):
                vel = to_vec3(vel(n))
            if callable(rot):
                rot = rot(n)
            if callable(scale):
                scale = scale(n)

        if pos is not None:
            self.position = pos
        if vel is not None:
            self.velocity = vel
        if scale is not None:
            self.scale(scale)
        if rot is not None:
            self.rotate(rot)

        if self.num is not None:
            if callable(pos):
                pos = pos(self.num)

        self._object = None
        self.object = kwargs.pop("obj", None) or kwargs.pop("object", None)

        each = kwargs.pop("each", None)
        if each:
            each(node=self, n=self.num)

        Scriptable.__init__(self)

        # register with partitioner on add/remove
        # def add():
        #     if self.partitioner:
        #         self.partitioner += self

        # self.on_add += add

        # def remove():
        #     if self.partitioner:
        #         self.partitioner -= self

        # self.on_remove += remove

    @property
    def on_deinit(self):
        if self._on_deinit is None:
            self._on_deinit = Signal()
        return self._on_deinit

    @property
    def on_update(self):
        if self._on_update is None:
            self._on_update = Signal()
        return self._on_update

    @property
    def event(self):
        if self._event is None:
            self._event = Events()
        return self._event

    # @property
    # def on_pend(self):
    #     if self._on_pend is None:
    #         self._on_pend = Signal()
    #     return self._on_pend

    @property
    def on_add(self):
        if self._on_add is None:
            self._on_add = Signal()
        return self._on_add

    @property
    def on_remove(self):
        if self._on_remove is None:
            self._on_remove = Signal()
        return self._on_remove

    @property
    def partitioner(self):
        return self._partitioner

    @property
    def visible(self):
        return self.invisible <= 0

    @visible.setter
    def visible(self, b):
        if b:
            self.invisible = 0
        else:
            self.invisible = 1

    @property
    def object(self):
        """
        get user object associated with this node (if any)
        """
        # unwrap weakref
        return self._object() if self._object else None

    @object.setter
    def object(self, obj):
        if self._object:
            self._object = weakref.ref(self._object)
        return self

    def tree(self, props="fvam"):
        r = {}
        r[str(self)] = {}
        rr = r[str(self)]
        if "p" in props:
            if not fcmp(self.pos):
                rr["pos"] = tuple(self.pos)
        if self.fn and "f" in props:
            rr["fn"] = self.fn
        if "v" in props:
            if self.vel and not fcmp(self.vel):
                rr["vel"] = tuple(self.vel)
        if "a" in props:
            if self.accel and not fcmp(self.accel):
                rr["accel"] = tuple(self.accel)
        if "m" in props:
            m = copy(self.matrix)
            m = tuple(tuple(x) for x in m)
            rr["matrix"] = m
        if self.children:
            rrr = rr["children"] = []
            for ch in self.children:
                rrr.append(ch.tree(props))
        return r

    def tag(self, t):
        if t.startswith("#"):
            t = t[1:]
        self.tags.add(t)

    def __bool__(self):
        """
        This is required to prevent python from checking len(node) for bool
        For ease of use, we want None to be the only false bool value
        """
        return True

    def __len__(self):
        return len(self.children)

    @property
    def size(self):
        if callable(self._size):
            return self._size()
        return self._size

    def walk_fast(self):
        if not self.frozen:
            yield self
        if not self.frozen_children:
            for ch in self.children:
                yield from ch.walk_fast()

    def __iter__(
        self,
        recursive=False,
        depth=None,
        include_self=False,
        only_self=False,
        ignore_frozen=False,
    ):
        if include_self:
            if not self.ignore_frozen or not self.frozen:
                yield self
        if not only_self:
            if depth is not None:
                depth -= 1
                if depth <= 0:
                    return
            if not self.ignore_frozen or not self.frozen_children:
                for ch in self.children:
                    yield from ch.__iter__(recursive, depth, True, not recursive)

    def walk(self):
        return self.__iter__(recursive=True)

    def each(self, func, recursive=False, depth=None, onlyself=False):
        for n in self.__iter__(recursive, depth, onlyself):
            func(n)

    def _calculate_world_box(self):
        lbox = self._local_box()
        if not lbox:
            return None
        r = Box()
        for i, v in enumerate(lbox):  # min, max
            r[i] = (self.world_matrix * vec4(v, 1)).xyz
        return r

    def calculate_vertices(self, recursive=False):
        r = []
        if recursive:
            for ch in self.children:
                r += ch.calculate_vertices(recursive=recursive)
        return r

    def _calculate_world_matrix(self):
        if self.parent:
            return self.parent.world_matrix * self.matrix
        else:
            return self.matrix

    # LOCAL <-> WORLD

    def orient_world_to_local(self, vec):
        return vec3(glm.inverse(self.world_matrix) * vec4(to_vec3(vec), 0))

    def world_to_local(self, pos):
        return vec3(glm.inverse(self.world_matrix) * vec4(to_vec3(pos), 1))

    def orient_local_to_world(self, vec):
        return vec3(self.world_matrix * vec4(to_vec3(vec), 0))

    def local_to_world(self, pos):
        return vec3(self.world_matrix * vec4(to_vec3(pos), 1))

    # # PARENT <-> LOCAL

    # def orient_from_parent(self, vec):
    #     return vec3(self.parent_world_matrix * vec4(to_vec3(vec),0))

    # def from_parent(self, pos):
    #     return vec3(self.parent_world_matrix * vec4(to_vec3(pos),1))

    # # local -> parent
    def orient_local_to_parent(self, vec):
        return vec3(self.matrix * vec4(to_vec3(vec), 0))

    def local_to_parent(self, pos):
        return vec3(self.matrix * vec4(to_vec3(pos), 1))

    # def orient_local_to_parent(self, vec):
    #     return vec3(glm.inverse(self.local_matrix) * vec4(to_vec3(vec),0))

    # def local_to_parent(self, pos):
    #     return vec3(glm.inverse(self.local_matrix) * vec4(to_vec3(pos),1))

    def orient_parent_to_local(self, vec):
        return vec3(self.local_matrix * vec4(to_vec3(vec), 0))

    def parent_to_local(self, pos):
        return vec3(self.local_matrix * vec4(to_vec3(pos), 1))

    # def orient_local_to_parent(self, vec):
    #     return vec3(glm.inverse(self.local_matrix) * vec4(to_vec3(vec),0))

    # def local_to_parent(self, pos):
    #     return vec3(glm.inverse(self.local_matrix) * vec4(to_vec3(pos),1))

    @property
    def world_box(self):
        return self._world_box()

    @property
    def world_min(self):
        return self._world_box()[0]

    @property
    def world_max(self):
        return self._world_box()[1]

    @world_box.setter
    def world_box(self, b):
        assert False  # not yet impl

    @property
    def local_box(self):
        return self._local_box()

    @local_box.setter
    def local_box(self, b):
        self._local_box(b)

    def set_local_box(self, b):
        self._local_box(b)

    # @box.setter
    # def box(self, b):
    #     self._box.set(b)

    @property
    def min(self):
        return self._local_box().min

    @property
    def max(self):
        return self._local_box().max

    # @min.setter
    # def min(self):
    #     self._local_box[0] = s

    # @max.setter
    # def max(self, s):
    #     self.box[1] = s

    def connect(self, sig, weak=True, on_remove=None, cb=None):  # for Lazy and Reactive
        return self.on_pend.connect(sig, weak, False, cb, on_remove)

    def disconnect(self, sig):  # for Lazy and Reactive
        self.on_pend -= sig
        self._matrix -= sig

    def __iadd__(self, c):
        # if isinstance(c, Component):
        #     # component
        #     self.components += c
        if type(c) in (tuple, list):
            for cc in c:
                self += cc
            return

        if isinstance(c, Slot):
            self.connections += c
        elif isinstance(c, str):
            if c.startswith("#"):
                c = c[1:]
                self.tags.add(c)
            else:
                self.add(c)
        elif callable(c):  # script?
            self.add_script(c)
        else:
            # on_pend signal
            self.on_pend += c
        return self

    def __isub__(self, c):
        # if isinstance(c, Component):
        #     # component
        #     self.components += c
        if isinstance(c, Slot):
            self.connections -= c
        elif isinstance(c, str):
            if c.startswith("#"):
                c = c[1:]
                try:
                    self.tags.remove(c)
                except KeyError:
                    pass
            else:
                self.remove(c)
        elif callable(c):  # script
            self.remove_script(c)
        else:
            # on_pend signal
            self.on_pend += c
        return self

    # def __isub__(self, con):
    # self.connections -= con

    def __enter__(self):
        return self.children.__enter__()

    def __exit__(self, typ, val, tb):
        return self.children.__exit__(typ, val, tb)

    def __getitem__(self, name):
        # warning: idx may change across frames
        if type(name) is int:  # name is idx
            return self.children[name]
        for ch in self.children:
            if ch.name == name:
                return ch
        raise IndexError

    @property
    def inherit_transform(self):
        return self._inherit_transform()

    @inherit_transform.setter
    def inherit_transform(self, b):
        self._inherit_transform(b)

    @property
    def matrix(self):
        return self._matrix()

    @matrix.setter
    def matrix(self, m):
        self._matrix(m)

    @property
    def local_matrix(self):
        return self._matrix()

    @property
    def parent_matrix(self):
        p = self.parent
        if p:
            self.parent.matrix
        return glm.mat4(1)

    @property
    def parent_world_matrix(self):
        p = self.parent
        if p:
            self.parent.world_matrix
        return glm.mat4(1)

    @local_matrix.setter
    def local_matrix(self, m):
        self._matrix(m)

    # @property
    # def matrix_func(self):
    #     return self._matrix_func()

    @property
    def world_matrix(self):
        if self.inherit_transform:
            return self._world_matrix()
        else:
            return self._matrix()

    # def matrix(self, space=PARENT):
    #     return matrix(self, parent)

    def rotate(self, turns, axis=ROTATION_AXIS):
        self._matrix(glm.rotate(self.matrix, turns * math.tau, axis))

    def stop(self):
        was_moving = bool(self.vel or self.accel)
        self.vel = None
        self.accel = None
        return was_moving

    @property
    def velocity(self):
        return self._vel or vec3(0)

    @property
    def v(self):
        return self.velocity

    @v.setter
    def v(self, *v):
        self.velocity = v

    @property
    def a(self):
        return self.acceleration

    @a.setter
    def a(self, *v):
        self.acceleration = a

    @velocity.setter
    def velocity(self, *v):
        if v is None:
            self._vel = None
            return None
        v = to_vec3(*v)
        if fcmp(v):
            self._vel = None
            return None
        self._vel = v
        return self._vel

    @property
    def vel(self):
        return self._vel or vec3(0)

    @vel.setter
    def vel(self, *v):
        self.velocity = v

    @property
    def acceleration(self):
        return self._accel or vec3(0)

    @acceleration.setter
    def accceleration(self, a):
        if a is None:
            return self._accel
        self._accel = a

    @property
    def accel(self):
        return self.acceleration

    @accel.setter
    def accel(self, *a):
        self.acceleration = a

    def reset_orientation(self, v=None, space=LOCAL):
        for i in range(3):
            self._matrix.value[i] = vec4(AXIS[i], 0)
            self._matrix.pend()

    # def decompose(self):
    #     pass

    # def reset_scale(self):

    # for i in range(3):
    #     self._matrix.value[i] = vec4(glm.normalize(self._matrix.value[i].xyz), 0)
    #     self._matrix.pend()

    def reset(self):
        self._matrix(mat4(1))

    def rescale(self, v=None, space=LOCAL):
        self.reset_scale()
        self.scale(v, space)

    def scale(self, *v, space=LOCAL):
        if v is None:
            assert False  #
        tv = type(v)
        if tv in (list, tuple):
            v = to_vec3(*v)
        elif tv in (int, float):
            v = vec3(float(v))
        if space == LOCAL:
            self._matrix.value *= glm.scale(mat4(1.0), v)
            self._matrix.pend()
        # elif space == PARENT:
        #     self._matrix.value = glm.scale(mat4(1.0), v) * self.matrix
        #     self.pend()
        else:
            assert False  # not impl

    def get_position(self, space=PARENT):
        if space == PARENT:
            return self._matrix()[3].xyz
        elif space == WORLD:
            return vec3(self._world_matrix()[3].xyz)
        assert False

    def set_position(self, p, space=None):
        assert space is None
        # if type(v) == int and space is None:
        #     space = v
        #     v = None
        # if space is None:
        #     space = PARENT
        # assert space == PARENT  # not impl
        self._matrix.value[3] = vec4(p, 1.0)  # set
        self._matrix.pend()
        return p

    @property
    def x(self):
        return self.position.x

    @x.setter
    def x(self, v):
        p = self.position
        self.position = vec3(v, p.y, p.z)
        return self

    @property
    def y(self):
        return self.position.y

    @y.setter
    def y(self, v):
        p = self.position
        self.position = vec3(p.x, v, p.z)

    @property
    def xy(self):
        return self.position.xy

    @xy.setter
    def xy(self, p):
        self.position = vec3(p.x, p.y, self.position.z)

    @property
    def z(self):
        return self.position.z

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

    @ax.setter
    def ax(self, v):
        p = self.acceleration
        self.acceleration = vec3(v, p.y, p.z)

    @property
    def ay(self):
        return self.acceleration.y

    @ay.setter
    def ay(self, v):
        p = self.acceleration
        self.acceleration = vec3(p.x, v, p.z)

    @property
    def az(self):
        return self.acceleration.y

    @az.setter
    def az(self, v):
        p = self.acceleration
        self.acceleration = vec3(p.x, p.y, v)

    @property
    def position(self):
        return self.get_position()

    @position.setter
    def position(self, *p):
        self.old_pos = self.position
        self.set_position(to_vec3(*p))

    @property
    def world_position(self):
        return self.set_position(WORLD)

    @property
    def pos(self):
        return self.get_position()

    @pos.setter
    def pos(self, *args):
        self.set_position(to_vec3(*args))

    @property
    def p(self):
        return self.get_position()

    @p.setter
    def p(self, *args):
        self.set_position(to_vec3(*args))

    @property
    def world_pos(self):
        return self.get_position(WORLD)

    @property
    def wpos(self):
        return self.get_position(WORLD)

    # def vec_to_local(self, v):
    #     v = vec4(v, 0)

    # @property
    # def angular_velocity(self):
    #     return self._spin

    # @angular_velocity.setter
    # def angular_velocity(self, angle):
    #     if fcmp(spin):
    #         self._spin = None
    #         return
    #     self._spin = angle

    # @property
    # def spin(self):
    #     return self._spin

    # @spin.setter
    def spin(self, angle=DUMMY, axis=Z):
        if angle is DUMMY:
            return self._spin
        if fcmp(angle):
            self._spin = None
            return
        self._spin = angle
        self.spin_axis = axis

    def move(self, *v):
        self._matrix.value[3] += vec4(to_vec3(*v), 0.0)
        self._matrix.pend()

    def pend(self):
        self._world_matrix.pend()
        self.on_pend()
        for ch in self.children:
            ch.pend()

    @property
    def root(self):
        return self._root() if self._root else None

    # @root.setter
    # def root(self, r):
    #     self._root = weakref.ref(r)

    @property
    def parent(self):
        return self._parent() if self._parent else None

    @parent.setter
    def parent(self, p):
        self._parent = weakref.ref(p)

    def attach(self, *args, **kwargs):
        if not args:
            raise Exception("No arguments to attach()?")
        elif args and callable(args[0]):
            return self.add_script(*args, **kwargs)
        if args and type(args[0]) is int:
            r = []
            for i in range(args[0]):
                r.append(self.app.create(*args[1:], **kwargs, num=i))
            cb = kwargs.get("cb", None)
            for i, node in enumerate(r):
                self.attach(node, cb=lambda slot: cb(slot, i))
            return r
        if args and isinstance(args[0], Node):
            cb = kwargs.get("cb", None)
            node = args[0]
            if node.parent:
                self.detach()

            def callback():
                if cb:
                    cb()
                node.pend()
                node.on_add()

            self.children.connect(node, cb=lambda *a: callback())
            node._parent = weakref.ref(self)
            node._root = self._root  # weakref
            return node
        else:
            cb = kwargs.pop("cb", None)
            return self.attach(self.app.create(*args, **kwargs), cb=cb)
        assert False

    def add(self, *args, **kwargs):  # alias for attach
        return self.attach(*args, **kwargs)

    # Implementing this will enable script on node
    # def script(self, dt):
    #     pass

    def update(self, dt):
        if self.frozen:
            return

        if self._spin is not None:
            # TODO: convert spin from spin space
            self.rotate(self._spin * dt, self.spin_axis)

        if self._accel is not None:
            self.velocity += self._accel * dt
        if self._vel is not None:
            self.position += self._vel * dt

        self.on_update(self, dt)

        # for component in self.components:
        #     component.update(self, dt)
        # for script in self.scripts:
        #     script.update(dt)
        Scriptable.update(self, dt)

        assert self.children._blocked == 0
        if not self.frozen_children:
            for ch in self.children:
                ch.update(dt)

        # if self.detach_me:
        #     detach_me = self.detach_me
        #     self.children = list(filter(lambda x: x not in detach_me, self.children)) #     self.detach_me = []
        #     for node in detach_me:
        #       e node.on_detach(node)

    def destroy(self):
        if not self.destroyed:
            self.destroyed = True

    # def safe_detach(self, func=None):
    #     if self.parent:
    #         self.parent.detach_me.append(self)
    #         if func:
    #             self.on_detach.connect(func, weak=False)

    def collapse(
        self,
        space=WORLD,
        new_parent=None,
        recursive=False,
        include_self=False,
        children=False,
        cb=None,
    ):
        """
        Collapse the node transform to world space and reconnect it to the root.
        If recursive is True, all children will be collapsed as well and
            returned along with this node in a list

        :param children: only collapse childen
        :param cb: since container operations can pend when blocked, provide callback when done
        """

        assert space != LOCAL
        if new_parent is None:
            new_parent = self.root if space == WORLD else self.parent
            if new_parent is None:
                # Already collapsed
                return None

        if include_self:
            self.detach(space=space, collapse=True)
        if recursive or children:
            if include_self:
                r = [self]
            else:
                r = []
            for ch in self.children:
                ch.collapse(space, new_parent, recursive, True, children=recursive)
                r.add(ch)
            if include_self:
                new_parent.add(self, cb=cb)
            return r

        return new_parent.add(self, cb=cb)

    def detach(self, node=None, collapse=False, inherit=True, reset=False, cb=None):
        """
        Detach a node from its parent and collapse its matrix into new_parent space (None means WORLD)
        If you wish to do that, call collapse()

        :param node: The child node to detach from self.  If node is None, detach self from parent.
        :param collapse: Will children be collapsed and reattached to parent?
        :param inherit: change local matrix into pre-detach world space
        :param reset: reset node matrix
        :param cb: callback continuation pending queued operations
        """
        if node is None:  # detach self

            parent = self.parent
            if parent is None:
                return

            lm = self.matrix
            if self.inherit_transform:
                wm = self.world_matrix

            if reset:
                self.reset()

            parent.detach(self, cb=cb)  # note: might be queued

            if (not reset) and inherit and self.inherit_transform:
                self.matrix = wm

            for ch in self.children:
                # collapse child transforms into parent space
                if inherit and ch.inherit_transform:
                    ch.matrix = lm * ch.matrix
                if collapse:
                    parent.attach(ch)

            self._parent = None
            return self
        else:  # node is not None, detach child

            if callable(node):
                return self.remove_script(node)  # node is actually a script

            # self.on_detach_child(node)
            # node.on_detach_self(self)
            if type(node) is int:
                self.children.disconnect(self.children[node], cb=cb)
            else:
                self.children.disconnect(node, cb=cb)
            node.on_remove()
            return node

    # def safe_remove(self, node=None):
    #     return self.safe_detach(node)

    def remove(self, node=None, collapse=True, inherit=False, reset=False, cb=None):
        return self.detach(node, collapse, inherit, reset, cb)

    def render(self):
        if self.children_visible:
            for ch in self.children:
                ch.render()

    def __str__(self):
        name = self.name or self.fn or ""
        typ = str(type(self).__name__)
        if name == typ:
            return name
        if typ:
            name = name + ":" + typ
        return name

    def find_if(self, func, recursive=True, one=False):
        for child in self.children:
            if func(child):
                yield child
                if one:
                    return
            if recursive:
                child.find_if(func, recursive)

    def find_by_type(self, typ, recursive=True):
        yield from self.find_if(lambda n: isinstance(n, typ), recursive)

    def find_by_tag(self, tag, recursive=True):
        if tag.startswith("#"):
            tag = tag[1:]
        yield from self.find_if(lambda n: tag in n.tags, recursive)

    def find_by_name(self, name, recursive=True):
        yield from self.find_if(lambda n: n.name == name, recursive)

    def find_by_filename(self, fn, recursive=True):
        yield from self.find_if(lambda n: n.fn == fn, recursive)

    def find_one(self, arg, recursive=True):
        return next(self.find(arg, recursive))

    def find(self, arg, recursive=True):
        if isinstance(arg, Node):  # name or tag
            if recursive:
                return [arg] if arg in self.walk() else []
            else:
                return [arg] if arg in self else []
        elif callable(arg):  # condition?
            yield from self.find_if(arg, recursive)
        elif isinstance(arg, str):  # name or tag
            if arg and arg[0] == "#":  # tag
                yield from self.find_by_tag(arg, recursive)
            else:
                if "." in arg:  # filename
                    yield from self.find_by_filename(arg, recursive)
                else:  # tag
                    yield from self.find_by_name(arg, recursive)
        elif arg == type:
            yield from self.find_by_type(arg, recursive)
        else:
            raise TypeError

    def __contains__(self, node):
        if callable(node):
            return bool(find_if(node))
        """
        Check if node is in children.  Not recursive.
        For recursive, use: `node in parent.walk()`
        """
        return node in self.children

    def draw(self):
        self.app.draw(self)

    def clear(self):
        for ch in self.children:
            ch.clear()
        self.children = Container()

    def cleanup(self):  # called by Core as an explicit destructor
        if not self.deinited:
            self.on_deinit()
            for ch in self.children:
                ch.cleanup()
            self.deinited = True

    # def __del__(self):
    # self.on_remove()
    # if self.app and self.app.partitioner:
    #     self.app.partitioner -= self

    @property
    def filename(self):
        return self.fn

    @filename.setter
    def filename(self, fn):
        self.fn = fn

    def _setup_world_matrix(self):
        self._world_matrix = Lazy(
            self._calculate_world_matrix,
            [
                self._matrix,
                self._inherit_transform,
                self,
            ],
        )

    def handle_collision(self, other):
        assert False


# class UserObject:
#     def __init__(self, node, *args, **kwargs)
#         self.node = node
