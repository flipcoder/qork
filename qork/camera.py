#!/usr/bin/python
from .node import *
from .canvas import *
from .audio import *
from .reactive import *
import glm
import math
from enum import Enum


class RenderLayer(Node):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, root=True, **kwargs)
        self.camera = self.add(Camera(app, mode="2D"))  # 2D hud view

        self.parent_camera = kwargs.get("camera", None)  # camera containing hud
        if self.parent_camera:
            self.parent_camera = weakref.ref(self.parent_camera)

        console = self.console = kwargs.get("console", None)
        if console:
            self.add(console)

        canvas = self.canvas = kwargs.get("canvas", None)
        if canvas:
            self.add(canvas)


class HUD(RenderLayer):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, root=True, **kwargs)


class Camera(Listener):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hud = None
        self.backdrop = None
        self._ortho = Reactive(True)

        self._use_ratio = Reactive(True)
        # left right botto top znear zfar
        self.ortho_bounds = Reactive([0.0, 1.0, -0.5, 0.5, -1.0, 1000.0])

        assert kwargs.get("projection", None) is None
        self.projection = Lazy(
            self.calculate_projection,
            [
                # dependencies
                self._ortho,
                self.ortho_bounds,
                self._use_ratio,
                self.app._size,
            ],
        )
        # self.connections += self.app.size.connect(self.projection)
        # FOV is specified in TURNS (use fov(deg(degrees)) for degrees)

        self._fov = Reactive(kwargs.get("fov", 0.1), [self.projection])
        self.view = Lazy(self.calculate_view, [self.on_pend])
        self.view_projection = Lazy(
            lambda self=self: self.projection() * self.view(),
            [self.projection, self.view]
            # [self.view_projection],
        )
        self.mode = kwargs.get("mode", "2D")  # !

        # self.connections += (
        #     self.projection.connect(self.app.view_projection.pend),
        #     self.view.connect(self.app.view_projection.pend)
        # )
        # self.connections += self.connect(self.app.view_projection.pend)

        self.camera_id = None
        # self.app.register_camera(self)
        self.pend()

        # associate camera with app so it can optimize transform caching
        # NOTE: cameras are registered even when they're not attached
        self.camera_id = None
        if self.app:
            self.app.register_camera(self)

        if kwargs.get("default", False):
            self.app.render_from(self)

    def __del__(self):
        if self.camera_id is not None:
            self.app.deregister_camera(self)

    def calculate_view(self):
        return glm.inverse(self.world_matrix)

    def calculate_projection(self):
        if self.ortho:
            if min(self.app.size) < 1:
                return glm.mat4(1)
            # ratio = self.app.size[0] / self.app.size[1]
            use_ratio = self._use_ratio()
            if use_ratio:
                ratio = self.app.aspect_ratio / 2
                return glm.ortho(-ratio, ratio, *self.ortho_bounds()[2:])
            else:
                return glm.ortho(*self.ortho_bounds())
        else:
            # ratio = self.app.size[0] / self.app.size[1]
            return glm.perspectiveFov(
                math.tau * self._fov(),
                self.app.aspect_ratio,  # float(self.app.size[0]),
                1,  # float(self.app.size[1]),
                0.01,
                1000.0,
            )

    @property
    def fov(self):
        return self._fov()

    @fov.setter
    def fov(self, v):
        """
        FOV angle is in TURNS, not degrees or radians.
        Use fov(util.deg(d)) or fov(util.rad(r)) if you prefer.
        """
        assert 0 < v < 1 + EPSILON
        self._fov(v)

    @property
    def ortho(self):
        return self._ortho()

    @ortho.setter
    def ortho(self, b):
        self._ortho(b)
        return b

    @property
    def perspective(self):
        return not self._ortho()

    @perspective.setter
    def perspective(self, b):
        self._ortho(not b)
        return b

    @property
    def mode(self, m):
        return "2D" if self.ortho else "3D"

    @mode.setter
    def mode(self, m):
        self.ortho = m == 2 or m[0] == "2"

    def update(self, dt):
        super().update(dt)

    def attach(self, *args, **kwargs):
        hud = args[0]
        if hud is RenderLayer:
            r = self.hud = self.add_hud()
            return r
        if args:
            if isinstance(hud, RenderLayer):
                r = self.hud = self.add_hud(hud)
                return r
        return super().attach(*args, **kwargs)

    def add(self, *args, **kwargs):  # alias for attach
        return self.attach(*args, **kwargs)

    def add_hud(self, node=None):
        if node is None:
            r = self._hud = RenderLayer(self.app, camera=self)
            return r
        elif isinstance(RenderLayer, node):  # hud node provided?
            node.parent_camera = weakref.ref(self)
            r = self._hud = node  # set RenderLayer to custom arg
            return r
        else:
            raise Exception("invalid RenderLayer provided")

    def remove_hud(self):
        self._hud = None

    def calculate_frustum(self):
        pass

    def in_frustum(box):
        pass
