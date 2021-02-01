#!/usr/bin/python3

import weakref
from .minimal import get_app_from_args


class Controller:
    def __init__(self, *args, **kwargs):
        self.app = get_app_from_args(args)
        self.num = None
        self.enabled = True

    def enable(self):
        self.enabled = True
    
    def disable(self):
        self.enabled = False
    
    def plug(self):
        """Register controller with engine"""
        if self.num is None:
            self.app.controllers += self
            self.num = self.app.controllers.get_id(self)

    def unplug(self):
        """Deregister controller with engine"""
        if self.num is not None:
            self.app.controllers -= self
            self.num = None

    def update(self, dt):
        pass

    def __del__(self):
        self.unplug()


class FPSController(Controller)
    def __init__(self, node, camera, *args, **kwargs):
        self.node = weakref.ref(node)
        self.camera = weakref.ref(camera)
    def update(self, dt):
        pass

class SpectatorController(Controller)
    def __init__(self, node, camera, *args, **kwargs):
        self.node = weakref.ref(node)
        self.camera = weakref.ref(camera)
    def update(self, dt):
        pass

class PlatformerController(Controller)
    def __init__(self, node, camera, *args, **kwargs):
        self.node = weakref.ref(node)
        self.camera = weakref.ref(camera)
    def update(self, dt):
        pass

class TopDownController(Controller)
    def __init__(self, node, camera, *args, **kwargs):
        self.node = weakref.ref(node)
        self.camera = weakref.ref(camera)
    def update(self, dt):
        pass

