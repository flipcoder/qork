#!/usr/bin/python3
from .minimal import get_app_from_args, StateBase
from .camera import Camera, RenderLayer


class State(StateBase):
    """
    State class for state stack
    """

    def __init__(self, name='', *args, **kwargs):

        # fix circular import
        from .scene import Scene
        from .camera import Camera, RenderLayer
        
        self.app = get_app_from_args(args)
        
        self.name = name

        self.scene = Scene("Scene", root=True)

        self.render_layer = RenderLayer(self.app, self.scene)
        
        self.camera = self.scene.add(Camera(default=True))

    def update(self, dt):
        self.scene.update(dt)

    def render(self):
        pass

    def deinit(self):
        pass

    @property
    def partitioner(self):
        return self.scene.partitioner
