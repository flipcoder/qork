#!/usr/bin/python3


class State:
    """
    State class for state stack
    """

    def __init__(self, *args, **kwargs):
        self.app = get_app_from_args(args)

    # def script(self, ctx):
    #     pass
    def update(self, t):
        pass

    def render(self):
        pass

    def deinit(self):
        pass
