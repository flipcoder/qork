#!/usr/bin/python3

from .resource import Resource
from .util import filename_from_args
from PIL import ImageFont


class Font(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font = ImageFont.truetype(self.fn, int(self.subpath))
