#!/usr/bin/env python

from .node import Node

from .easy import qork_app
from .resource import Resource
import pathlib

from openal import *

# import openal.loaders

# class AudioListener:
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


class Sound(Node):
    class Resource(Resource):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.ext == ".wav":
                self.data = oalOpen(self.fn)
                self.stream = False
            elif self.ext in (".mp3", ".ogg"):
                self.stream = self.app.on_update.connect(
                    WeakLambda([self], lambda t, self: self.data.update)
                )
                self.data = oalStream(self.fn)
            else:
                raise FileNotFound
            # elif ext == '.mp3'
            # elif ext == '.ogg'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.app.cache(self.fn)


class SoundSource(Node):
    def __init__(self, *args, loop=False, **kwargs):
        super().__init__(*args, **kwargs)


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
