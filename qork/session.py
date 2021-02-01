#!/usr/bin/python3

from .minimal import get_app_from_args

class Session:
    def __init__(self, *args, **kwargs):
        self.app = get_app_from_args(args)
    def update(self, dt):
        pass

