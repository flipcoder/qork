#!/usr/bin/env python

from qork.node import Node
from qork.partitioner import Partitioner


class Scene(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backdrop = None
        self.is_root = True
        self._partitioner = Partitioner(self)
    def update(self, dt):
        self._partitioner.update(dt)
        super().update(dt)

