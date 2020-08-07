#!/usr/bin/env python

from .node import Node

from .easy import qork_app
from .resource import Resource
from .util import *
from .signal import *
import pathlib

import openal

# import openal.loaders


class Listener(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.listener = openal.Listener()
        # self += self._update_listener

    def _update_listener(self):
        pass


class Sound(Node):
    class Resource(Resource):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            if self.ext == ".wav":
                # self.data = openal.oalOpen(self.fn)
                self.data = openal.Buffer(openal.WaveFile(self.fn))
                self.stream = False
            elif self.ext in (".mp3", ".ogg"):
                self.data = openal.oalStream(self.fn)
                # print(self.data)
                # self.stream = self.app.on_update.connect(
                #     self.data.update
                #     # WeakLambda([self], lambda t, self: self.data.update)
                # )
            elif not self.ext:
                self.data = None
                self.stream = False
                pass  # empty sound
            else:
                raise ValueError("invalid audio filetype")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.ext == ".wav":
            self.data = self.app.cache(self.fn)
            self.source = openal.Source(self.data.data)
            self._loop = kwargs.pop("loop", False)
        else:  # stream
            self.data = Sound.Resource(self.fn)
            self.source = self.data.data
            self._loop = kwargs.pop("loop", True)

        self.temp = kwargs.pop("temp", False)
        self.on_done = Signal()

        self.played = 0
        self.play()

    @property
    def loop(self, b):
        pass

    def play(self, fn=None, once=False, temp=False):
        if temp:
            self.temp = temp
        self.source.play()
        self.played += 1
        return True

    def update(self, dt):
        if self.source:
            self.source.update()
        if self.on_done or self.temp:
            if self.source.get_state() != openal.AL_PLAYING:
                self.on_done()
                if self.temp:
                    self.remove()

    # class SoundSource(Node):
    #     def __init__(self, *args, loop=False, **kwargs):
    #         super().__init__(*args, **kwargs)


class Audio:
    def __init__(self, app):
        self.app = app or qork_app()
        # self.sink = openal.audio.SoundSink()

    def update(self, dt):
        pass
        # self.sink.update()

    def play(self, source):
        source.play()
        # self.sink.play(source)
