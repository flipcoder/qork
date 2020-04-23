#!/usr/bin/env python

from .node import Node

from .easy import qork_app
from .resource import Resource

import openal
import openal.audio
# import openal.loaders

class SoundBuffer(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ext = self.fn[:-4].lower()
        if ext == '.wav':
            self.data = openal.loaders.load_wav_file(self.fn)
        else:
            raise FileNotFound
        # elif ext == '.mp3'
        # elif ext == '.ogg'

# class AudioListener:
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

class Sound(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SoundSource(Node):
    def __init__(self, *args, loop=False, **kwargs):
        super().__init__(*args, **kwargs)

class Audio:
    def __init__(self, app):
        self.app = app or qork_app()
        self.sink = openal.audio.SoundSink()
    def update(self, dt):
        self.sink.update()
    def play(self, source):
        self.sink.play(source)

