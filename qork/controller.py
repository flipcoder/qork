#!/usr/bin/python3

from .minimal import get_app_from_args


class Controller:
    def __init__(self, *args, **kwargs):
        self.app = get_app_from_args(args)
        self.num = None

    def plug(self):
        if self.num is None:
            self.app.controllers += self
            self.num = self.app.controllers.get_id(self)

    def unplug(self):
        if self.num is not None:
            self.app.controllers -= self
            self.num = None

    def update(self, dt):
        pass

    def __del__(self):
        self.unplug()

