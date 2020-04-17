#!/usr/bin/env python
import glm
import sys

# if __debug__:
#     sys.argv += ['--vsync','off']
import moderngl as gl
import moderngl_window as mglw
from .corebase import *
from .sprite import *
from .defs import *
from .cache import *
from .util import *
from .node import *
from .mesh import *
from .reactive import *
from .signal import *
from .partitioner import *
from .canvas import *
from .corebase import *
from .easy import qork_app
import cson
import os
from os import path
from collections import defaultdict
from dataclasses import dataclass

# class RenderPass
#     def __init__(self, camera):
#         self.camera = camera


def cson_load(fn):
    with open(fn) as f:
        return cson.load(f)


def _try_load(fn, paths, func, *args, **kwargs):
    """
    Try to load filename `fn` for given `paths`
    Func should be a load function that takes a filename and optionally
      args and kwargs, which are forwarded to the function
    """
    r = None
    for p in paths:
        try:
            print(path.join(p, fn))
            r = func(path.join(p, fn), *args, **kwargs)
        except FileNotFoundError:
            continue
        break
    if not r:
        raise FileNotFoundError
    return r


class Core(mglw.WindowConfig, Partitioner, CoreBase):
    gl_version = (3, 3)
    window_size = (960, 540)
    aspect_ratio = 16 / 9
    resizable = True
    samples = 4
    title = "qork"
    # resource_dir = os.path.normpath(os.path.join(__file__, '../../data/'))

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)

    # def data_path(self, p=None):
    #     if p is None:
    #         return self._data_path
    #     folder = self.script_path or sys.argv[0]
    #     self._data_path = path.join(path.dirname(path.realpath(folder)), p)
    #     return self._data_path

    def _data_path(self, p):
        folder = self.script_path or sys.argv[0]
        dp = path.join(path.dirname(path.realpath(folder)), p)
        self._data_paths.append(dp)
        return dp

    def data_path(self, p=None):
        if p is None:
            return self._data_paths
        if isinstance(p, (list, tuple)):
            for dp in p:
                self._data_path(dp)
        else:
            self._data_path(p)
        return self._data_path

    def data_paths(self, p):
        self.data_paths = []  # reset
        return self.data_path(p)

    def __init__(self, **kwargs):
        self.script_path = None  # script path is using script
        self.cache = Cache(self.resolve_resource, self.transform_resource)

        qork_app(self)

        self.wnd = kwargs.get("wnd")
        self.ctx = kwargs.get("ctx")
        self.timer = kwargs.get("timer")

        # super(mglw.WindowConfig, self).__init__(self)
        Partitioner.__init__(self)

        self._size = Reactive(ivec2(*self.window_size))
        self._data_paths = []
        self.data_paths([".", "data"])
        # self.on_resize = Signal()
        self.on_update = Signal()
        # self.on_quit = Signal()
        # self.on_render = Signal()
        # self.on_collision_enter = Signal()
        # self.on_collision_leave = Signal()
        # self.cleanup_list = []  # nodes awaiting dtor/destuctor/deinit calls
        self.world = Node()
        self.world.is_root = True
        self.gui = None
        self.renderfrom = self.camera = None  # default 3d camera
        self._view = None  # default gui camera
        self.bg_color = (0, 0, 0)
        self.view_projection = Lazy(lambda: self.projection() * self.view())
        # self.renderpass = RenderPass()
        # self.create = Factory(self.resolve_entity)
        self.state = None

        # signal dicts
        class SwitchSignal:
            def __init__(self):
                self.on_press = Signal()
                self.on_release = Signal()
                self.while_pressed = Signal()

        self.key_events = defaultdict(SwitchSignal)
        self.mouse_events = defaultdict(SwitchSignal)

        self.on_unicode = Signal()  # unicode keyboard char
        self.on_scroll = Signal()  # mouse wheel x, y

        self.keys = set()
        self.keys_pressed = set()
        self.keys_released = set()

        self.mouse = vec2(0)
        self.mouse_delta = vec2(0)

        self.mouse_buttons = set()
        self.mouse_pressed = set()
        self.mouse_released = set()

        self.K = self.wnd.keys

        super(Partitioner, self).__init__()

    @property
    def size(self):
        return self.window_size

    # event
    def resize(self, w, h):
        self._size(ivec2(w, h))

    # event
    def close(self):
        pass

    def iconify(self, a):
        pass

    def unicode_char_entered(self, s):
        self.on_unicode(s)

    def get_mouse_scroll_event(self, x, y):
        self.on_scroll(x, y)

    def get_mouse_position_event(self, x, y, dx, dy):
        self.mouse = vec2(x, y)
        self.mouse_delta = vec2(dx, dy)
        self.on_mouse_move(x, y, dx, dy)

    def get_mouse_buttons(self):
        return self.mouse_buttons

    def get_mouse_buttons_released(self):
        return self.mouse_released

    def get_mouse_buttons_pressed(self):
        return self.mouse_pressed

    def hold_click(self, k=0):
        return k in self.mouse_buttons

    def unclick(self, k=0):
        return k in self.mouse_released

    def click(self, k=0):
        return k in self.mouse_pressed

    def get_key(self, k):
        return k in self.keys

    def get_key_pressed(self, k):
        return k in self.keys_pressed

    def get_key_released(self, k):
        return k in self.keys_released

    def get_keys(self):
        return self.keys

    def get_keys_pressed(self):
        return self.keys_pressed

    def get_keys_released(self):
        return self.keys_released

    def key_event(self, key, action, mod):
        if action == self.K.ACTION_PRESS:
            self.keys_pressed.add(key)
            self.keys.add(key)
            self.key_events[key].on_press()
        elif action == self.K.ACTION_RELEASE:
            self.keys_released.add(key)
            self.keys.remove(key)
            self.key_events[key].on_release()

    def mouse_press_event(self, x, y, btn):
        self.mouse_pressed.add(btn)
        self.mouse_buttons.add(btn)
        self.mouse_events[btn].on_press(btn)

    def mouse_release_event(self, x, y, btn):
        self.mouse_released.add(btn)
        self.mouse_buttons.remove(btn)
        self.mouse_events[btn].on_release(btn)

    def create(self, *args, **kwargs):
        if args and isinstance(args[0], int):
            r = []
            args = list(args)
            count = args[0]
            args = args[1:]  # pop count from arg list
            for c in range(count):
                r.append(self.create(*args, **kwargs))
            return r
        if not args:
            return Node(*args, **kwargs)
        if isinstance(args[0], Node):
            return args[0]
        fn = filename_from_args(args, kwargs)
        if fn:
            return Mesh(*args, **kwargs)
        elif isinstance(args[0], tuple):  # prefab data
            return Mesh(*args, **kwargs)
        else:
            return Node(*args, **kwargs)

    def add(self, *args, **kwargs):
        if args and isinstance(args[0], int):  # count
            r = []
            count = args[0]
            args = list(args)
            args = args[1:]
            for c in range(count):
                node = self.create(*args, num=c, **kwargs)
                r.append(self.world.add(node))
            return r
        return self.world.add(self.create(*args, **kwargs))

    def update(self, t):

        if t < 0.0:
            return

        for key in self.keys:
            self.key_events[key].while_pressed(key, t)

        for btn in self.mouse_buttons:
            self.mouse_events[btn].while_pressed(btn, t)

        if self.state:
            self.state.update(t)

        Partitioner.update(self, t)

        self.on_update(t)

        self.world.update(t)

    def post_update(self, t):

        self.keys_pressed.clear()
        self.keys_released.clear()
        self.mouse_pressed.clear()
        self.mouse_released.clear()

    def transform_resource(self, *args, **kwargs):
        args = [self] + list(args)
        return args, kwargs

    def resolve_resource(self, *args, **kwargs):
        fn = filename_from_args(args, kwargs)
        assert fn
        fnl = fn.lower()
        for ext in [".cson"]:
            data = None
            try:
                data = _try_load(fn, self._data_paths, cson_load)
            except FileNotFoundError:
                return None, None, None
            if data:
                if data["type"] == "sprite":
                    return Sprite, args, kwargs
                data.close()
            else:
                raise FileNotFoundError
        for ext in [".png", ".jpg"]:
            if fnl.endswith(ext):
                return Image, args, kwargs
        return None, None, None

    def render(self, time, dt):
        """
        Due to moderngl method naming, this is technically both logic and render
        (update and render are separate everywhere else)
        But this does an entire game frame: both update(t) and render() here
        """
        if dt < 0.0:
            return
        self.dt = dt
        self.time = time
        self.update(dt)
        self.post_update(dt)
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(gl.DEPTH_TEST | gl.CULL_FACE)
        if self.world and self.camera:
            self.renderfrom = self.camera
            self.world.render()
        if self.gui and self.view:
            self.renderfrom = self._view
            self.gui.render()
        self.renderfrom = None

    # def view_projection(self):
    #     return self.projection() * self.view()

    # def camera(self):
    #     return self._camera

    def projection(self):
        return self.renderfrom.projection()

    def view(self):
        return self.renderfrom.view()

    def matrix(self, m):
        self.shader["ModelViewProjection"] = flatten(self.view_projection() * m)
