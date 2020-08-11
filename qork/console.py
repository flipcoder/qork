#!/usr/bin/env python

from qork.canvas import Canvas


class Console(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
