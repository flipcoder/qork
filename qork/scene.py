#!/usr/bin/env python

from qork.node import *


class Scene(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backdrop = None
