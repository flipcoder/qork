#!/usr/bin/python3
from .minimal import get_app_from_args, StateBase
from .camera import Camera, RenderLayer
from glm import ivec2
from .scriptable import Scriptable


class State(StateBase):
    """
    State class for state stack
    """

    def __init__(self, name="", init=True, *args, **kwargs):
        from .scriptable import Scriptable
        Scriptable.__init__(self)

        # fix circular import
        from .scene import Scene

        self.app = get_app_from_args(args)
        
        # set this temporarily so add()s will work during ctors
        # on_pending_state signal inside of StateStack registered by Core
        # will unset this
        self.app.pending_state = self

        self.name = name

        self.scene = Scene("Scene", root=True)

        self.render_layer = RenderLayer(self.app, self.scene)

        self.camera = self.scene.add(Camera(default=True))

        if init:
            self._init()

    def _init(self):
        from .camera import Camera, RenderLayer
        from .canvas import Canvas

        self.canvas_layer = self.camera.add(RenderLayer)
        self.canvas = self.canvas_layer.canvas = self.canvas_layer.add(
            Canvas(self, res=ivec2(1920, 1080), scale=self.app.scale)
        )

        # TODO: add signal on resize
        # self.console_layer = camera.add(RenderLayer)
        # self.console = self.console_layer.console = self.console_layer.add(Canvas(self, res=ivec2(1920,1080), scale=self.scale))

        self.backdrop_layer = self.scene.backdrop = RenderLayer(
            self, camera=self.camera
        )
        self.backdrop = self.backdrop_layer.canvas = self.backdrop_layer.add(
            Canvas(self, res=ivec2(1920, 1080), scale=self.app.scale)
        )

        if hasattr(self, 'script'):
            self.add_script(self.script)

    def update(self, dt):
        Scriptable.update(self, dt)
        self.scene.update(dt)

    def add_script(self, s):
        return Scriptable.add_script(self, s)

    def remove_script(self, s):
        return Scriptable.remove_script(self, s)

    def render(self):
        pass

    def deinit(self):
        pass

    @property
    def partitioner(self):
        return self.scene.partitioner
