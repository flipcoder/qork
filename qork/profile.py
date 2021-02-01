#!/usr/bin/python

from .minimal import get_app_from_args

class Profile:
    """
    Player information & controller
    """
    def __init__(self, *args, **kwargs):
        self.app = get_app_from_args(args)
        self.default = kwargs.get('default', False)
        self.num = None

    # def update(self, dt):
    #     pass

    def enable(self):
        if self.num is None:
            self.app.profiles += self
            self.num = self.app.profiles.get_id(self)

    def disable(self):
        if self.num:
            self.app.profiles -= self
            self.num = None

