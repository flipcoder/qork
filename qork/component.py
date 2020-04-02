#!/usr/bin/env python


class Component:
    def __init__(self, node):
        self.node = node

    def script(self, ctx):
        pass

    def update(self, dt):
        pass

    def render(self):
        pass
