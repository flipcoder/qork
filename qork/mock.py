#!/usr/bin/python3
from .easy import qork_app


def get_app_from_args(args):
    app = None
    if args:
        arg0 = args[0]

        if isinstance(arg0, CoreBase):
            app = self.app = arg0
        else:
            app = self.app = qork_app()
    else:
        app = self.app = qork_app()
    
    if app is None:
        app = self.app = MockApp()

class MockApp:
    def __init__(self):
        self.cache = None
        self.ctx = None
        self.partitioner = None

    def create(self, *args, **kwargs):
        return Node(*args, **kwargs)
