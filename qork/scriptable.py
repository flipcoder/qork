#!/usr/bin/python3

from .signal import Signal
from .script import Script

class Scriptable:
    def __init__(self):
        self.scripts = Signal()

    def update(self, dt):
        if self.scripts:
            self.scripts.each(lambda x, dt: x.update(dt), dt)
            self.scripts._slots = list(
                filter(lambda x: not x.get().done(), self.scripts.slots)
            )

    def add_script(self, script, weak=False):
        return self.scripts.connect(Script(script, self), weak=weak)

    def remove_script(self, script):
        self.scripts -= Script(script, self)

