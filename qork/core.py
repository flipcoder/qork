#!/usr/bin/env python
import glm
import sys

# if __debug__:
#     sys.argv += ['--vsync','off']
import moderngl as gl
# import moderngl_window
import moderngl_window as mglw
# from moderngl_window.intergrations import imgui as ImguiWindow
from .corebase import *
from .reactive import *
from .signal import *
from .sprite import *
from .defs import *
from .cache import *
from .util import *
from .node import *
from .mesh import *
from .partitioner import *
from .canvas import *
from .corebase import *
from .camera import *
from .when import *
from .audio import *
from .easy import qork_app
import cson
import os
from os import path
from collections import defaultdict

# class RenderPass
#     def __init__(self, camera):
#         self.cam = camera


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
            r = func(path.join(p, fn), *args, **kwargs)
        except FileNotFoundError:
            continue
        break
    if not r:
        raise FileNotFoundError
    return r


class Core(mglw.WindowConfig, CoreBase):
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
            self._data_paths = []  # reset
            for dp in p:
                self._data_path(dp)
        else:
            self._data_path(p)
        return self._data_path

    def data_paths(self, p=DUMMY):
        if p is DUMMY:
            return self._data_paths
        self._data_paths = []  # reset
        return self.data_path(p)

    def __init__(self, wnd=None, ctx=None, **kwargs):
        super().__init__(wnd=wnd, ctx=ctx, **kwargs)
        
        self.script_path = None  # script path is using script
        self.cache = Cache(self.resolve_resource, self.transform_resource)

        qork_app(self)

        self.wnd = wnd
        self.ctx = ctx
        # self.timer = kwargs.get("timer")

        # super(mglw.WindowConfig, self).__init__(self)

        self.audio = Audio(self)

        self.when = When()
        self._size = Reactive(ivec2(*self.window_size))
        self._data_paths = []
        self.data_paths([".", "data"])
        # self.on_resize = Signal()
        self.connections = Connections()
        self.on_update = Signal()
        # self.on_quit = Signal()
        # self.on_render = Signal()
        # self.on_collision_enter = Signal()
        # self.on_collision_leave = Signal()
        # self.cleanup_list = []  # nodes awaiting dtor/destuctor/deinit calls
        
        self.partitioner = Partitioner(self)
        
        self.scene = Node('Scene', root=True)
        self.gui = None
        self.renderfrom = None
        self._view = None  # default gui camera
        self.bg_color = (0, 0, 0)
        
        # self.renderpass = RenderPass()
        # self.create = Factory(self.resolve_entity)
        self.states = Container(reactive=True) # state stack

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

        self.mouse_pos = vec2(0)
        self.mouse_delta = vec2(0)

        self.mouse_buttons = set()
        self.mouse_pressed = set()
        self.mouse_released = set()

        self.K = self.wnd.keys

        self.view_projection = Lazy(lambda: self.projection() * self.view())
        
        self.camera = self.scene.add(Camera()) # requires view/proj above

        # self.renderpass = RenderPass()
        # self.renderpass.app = self

    @property
    def state(self):
        try:
            return self.states[-1]
        except IndexError:
            return None
        
    @property
    def size(self):
        return self.window_size # TODO: get size?

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
        self.mouse_pos = vec2(x, y)
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
            try:
                self.keys.remove(key)
            except KeyError:
                pass
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
                r.append(self.scene.add(node))
            return r
        return self.scene.add(self.create(*args, **kwargs))

    def update(self, dt):
        if not self.partitioner:
            return

        for key in self.keys:
            self.key_events[key].while_pressed(key, dt)

        for btn in self.mouse_buttons:
            self.mouse_events[btn].while_pressed(btn, dt)

        self.audio.update(dt)
        self.partitioner.update(dt)

        self.when.update(dt)
        self.on_update(dt)

        if self.state:
            self.state.update(dt)
        else:
            self.scene.update(dt)

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
        if dt <= 0:
            # dt is a huge negative number at the beginning
            # ignore it
            return
        
        self.dt = dt
        # self.time = time
        self.update(dt)
        self.post_update(dt)
        
        if self.state:
            self.state.render(dt)
            return

        self.clear()
        assert self.camera
        if self.camera and self.scene:
            self.draw(self.camera, self.scene)
        else:
            assert self.camera
            assert self.scene
        if self._view and self.gui:
            self.draw(self._view, self.gui)
        
    def clear(self, color=None):
        if color is None:
            color = self.bg_color
        self.ctx.clear(*color)
        self.ctx.enable(gl.DEPTH_TEST | gl.CULL_FACE)
    
    def draw(self, camera, root=None):
        if root is None:
            root = camera.root
            if not root:
                return
        
        self.renderfrom = camera
        root.render()
        self.renderfrom = None

    # def view_projection(self):
    #     return self.projection() * self.view()

    # @property
    # def camera(self):
    #     return self.cam()

    def projection(self):
        # self.renderfrom.projection.pend()
        return self.renderfrom.projection()

    def view(self):
        # self.renderfrom.view.pend()
        return self.renderfrom.view()

    def matrix(self, m):
        self.shader["ModelViewProjection"] = flatten(self.view_projection() * m)


