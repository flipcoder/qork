#!/usr/bin/env python

from .node import Node
from .partitioner import Partitioner
from .minimal import get_app_from_args


class Scene(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = get_app_from_args(args)
        self.backdrop = None
        self._partitioner = Partitioner(self)

    def update(self, dt):
        self._partitioner.update(dt)
        super().update(dt)

