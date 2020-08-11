#!/usr/bin/env python
import glm
import sys

# if __debug__:
#     if {"--vsync", "-vs"} & set(sys.argv):
#         sys.argv += ["--vsync", "off"]

import moderngl as gl

# import moderngl_window
import moderngl_window as mglw
import pathlib

# from moderngl_window.intergrations import imgui as ImguiWindow
from .corebase import *
from .reactive import *
from .signal import *
from .sprite import *
from .defs import *
from .cache import *
import qork.util
from .util import *
from .node import *
from .mesh import *
from .partitioner import *
from .canvas import *
from .camera import *
from .when import *
from .audio import *
from .box import *
from .tilemap import *
from .easy import qork_app
from .scene import *
import cson
import os
from os import path
from collections import defaultdict
from watchdog.observers import Observer as Watchdog
import openal

# class RenderPass
#     def __init__(self, camera):
#         self.cam = camera


class ImageResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = Image.open(self.fn)


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
    window_size = (1920, 1080)
    aspect_ratio = 16 / 9
    resizable = True
    samples = 2
    title = "qork"
    vsync = False
    # resource_dir = os.path.normpath(os.path.join(__file__, '../../data/'))

    Resource = {"mesh": Mesh.Resource, "sound": Sound.Resource, "sprite": Sprite}  # !

    # Which cson type is handled by which class?
    Type = {"mesh": Mesh, "sound": Sound, "sprite": Mesh, "tilemap": TileMap}  # !

    # Node types and their associated extensions
    extensions = {
        "sound": [".wav", ".mp3", ".ogg", ".flac"],
        "mesh": [".obj"],
        "sprite": [".png", ".jpg"],
        "tilemap": [".tmx"],
    }

    @staticmethod
    def sys_start():
        openal.pyoggSetStreamBufferSize(4096 * 4)
        openal.oalSetStreamBufferCount(4)

    def sys_stop():
        openal.oalQuit()

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

        self.scene = Scene("Scene", root=True)
        self.render_layer = RenderLayer(self, self.scene)
        self.gui = None
        self.renderfrom = None
        self._view = None  # default gui camera
        self._bg_color = vec4(0, 0, 0, 0)

        # self.renderpass = RenderPass()
        # self.create = Factory(self.resolve_entity)
        self.states = Container(reactive=True)  # state stack

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

        self.golfing = True

        self.viewport = Box()

        self.K = self.wnd.keys

        self.view_projection = {} # 

        self.camera = self.scene.add(Camera())  # requires view/proj above
        self.next_camera_id = 0

        self.watch = Watchdog()

        # self.renderpass = RenderPass()
        # self.renderpass.app = self

    def register_camera(self, camera):
        if camera.camera_id is None:
            cam_id = camera.camera_id = self.next_camera_id
            self.next_camera_id += 1
            self.view_projection[cam_id] = Lazy(WeakLambda(cam, lambda: cam.projection() * cam.view()))
        camera.pend()

    @property
    def state(self):
        try:
            return self.states[-1]
        except IndexError:
            return None

    @property
    def size(self):
        return self._size()

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
        if args:
            a = args[0]
            atype = type(args[0])
            if atype is int:
                count = a
                each = kwargs.pop("each", None)
                # load a count of objects
                r = []
                args = list(args)
                args = args[1:]  # pop count from arg list
                for c in range(count):
                    if each:
                        kwargs["each"] = lambda node=node, each=each: each(node, count)
                    r.append(self.create(str(count), *args, **kwargs))
                return r
            elif atype in (tuple, list):
                filenames = a
                each = kwargs.pop("each", None)
                # load a list of filenames
                r = []
                args = list(args)
                args = args[1:]
                if each:
                    for fn in filenames:
                        # func, aa, kw = each(count, *copy(args), **copy(kwargs))
                        if each:
                            kwargs["each"] = lambda node=node, each=each: each(node)
                        r.append(self.create(fn, *args, **kwargs))
                else:
                    for fn in filenames:
                        r.append(self.create(fn, *args, **kwargs))
                return r
        if not args:
            return Node(*args, **kwargs)
        if isinstance(args[0], Node):
            return args[0]
        fn = filename_from_args(args, kwargs)
        try:
            ext = pathlib.Path(fn).suffix
        except TypeError:
            ext = ''
        if ext:
            for typename, typelist in self.extensions.items():
                if ext in typelist:
                    return self.Type[typename](*args, **kwargs)
        else:
            return Node(*args, **kwargs)
            # if self.golfing:  # codegolf?: try to find filename
            #     found = False
            #     for dp in self._data_paths:
            #         # TODO: prioritize .cson?
            #         if path.exists(fn + ".cson"):
            #             fn += ".cson"
            #             found = True
            #             break
            #         for pth in os.listdir(dp):
            #             pext = path.splitext(pth)
            #             if pext[0] == fn:
            #                 fn += pext[1]
            #                 found = True
            #                 break
            #         if found:
            #             break
            #     if found:
            #         args, kwargs = change_filename(fn, args, kwargs)

        if fn:
            return Mesh(*args, **kwargs)
        else:
            return Node(*args, **kwargs)

        # if ext in ('.wav', '.mp3', '.ogg'):
        #     return Sound(*args, **kwargs)
        # elif fn:
        #     return Mesh(*args, **kwargs)
        # elif isinstance(args[0], tuple):  # prefab data
        #     return Mesh(*args, **kwargs)
        # else:
        #     return Node(*args, **kwargs)

    def play(self, fn, **kwarg):
        """
        Quick-play a sound
        """
        return camera.add(fn, temp=True)

    def add(self, *args, **kwargs):
        if args and isinstance(args[0], int):  # count
            r = [None] * args[0]
            count = args[0]
            args = list(args)
            args = args[1:]
            for i in range(count):
                node = self.create(*args, num=i, **kwargs)
                r[i] = self.scene.add(node)
            return r
        return self.scene.add(self.create(*args, **kwargs))

    def __iadd__(self, node):
        self.add(node)
        return self

    def __isub__(self, node):
        self.remove(node)
        return self

    def remove(self, *args, **kwargs):
        self.scene.remove(*args, **kwargs)

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
        ext = pathlib.Path(fn.lower()).suffix
        T = kwargs.pop("T", None)  # type
        if T:
            return self.Type[T], args, kwargs
        if ext in [".mp3", ".wav", ".ogg"]:
            return Sound.Resource, args, kwargs
        elif ext == ".cson":
            data = None
            try:
                data = _try_load(fn, self._data_paths, cson_load)
            except FileNotFoundError:
                return None, None, None
            if data:
                if data["type"] == "sprite":
                    return Sprite, args, kwargs  # !
                elif data["type"] == "sound":
                    return Sound.Resource, args, kwargs
                elif data["type"] == "mesh":
                    return Mesh.Resource, args, kwargs
                data.close()
            else:
                raise FileNotFoundError()
        elif ext in [".png", ".jpg"]:
            return ImageResource, args, kwargs
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

        self.render_clear()
        assert self.camera
        
        scene = self.scene
        
        if scene and scene.skybox:
            self.draw(scene.skybox.camera, scene.skybox)
            self.render_clear_depth()
        
        if self.camera and self.scene:
            self.draw(self.camera, self.scene)
        else:
            assert self.camera
            assert self.scene

        if self.camera.hud:
            hud = self.camera.hud
            self.render_clear_depth()
            self.draw(hud.camera, hud)
        
        # if self._view_camera and self.view_hud:
        #     self.draw(self._view_camera, self.view_hud)

    def render_clear_depth(self):
        ctx = self.ctx
        fbo = ctx.fbo
        fbo.color_mask = False, False, False, False
        ctx.clear()
        fbo.color_mask = True, True, True, True
    
    def clear(self):
        if self.state():
            return self.state.clear()
        self.scene.clear()
        return

    def background(self, col=DUMMY):
        if col is DUMMY:
            return self._bg_color
        self._bg_color = Color(col)
        return col

    def render_clear(self, col=None):
        if col is None:
            col = self._bg_color
        else:
            col = Color(col)
        self.ctx.clear(col[0], col[1], col[2])
        self.ctx.enable(gl.DEPTH_TEST | gl.CULL_FACE)

    def draw(self, camera, root=None, viewport=None):
        
        if root is None:
            root = camera.root
            if not root:
                return
        if viewport is None:
            viewport = self.viewport

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
        self.mvp_uniform.value = flatten(
            self.renderfrom.view_projection() * m
        )

    def golf(self):
        if self.golfing:
            return

        # TODO: codegolf method names
        methods = {
            "A": self.add,
            "R": self.remove,
            "P": self.play,
            "C": self.scene.clear,
        }
        for k, v in methods.items():
            setattr(cls, k, v)

        self.golfing = b

    def destroy(self):
        if self.ctx:
            openal.oalQuit()
            del self.ctx

    def quit(self):
        return self.destroy()

    def __del__(self):
        self.destroy()
