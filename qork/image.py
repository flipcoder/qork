#!/usr/bin/python3

from .resource import Resource
from PIL import Image


class ImageResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = Image.open(self.full_fn)
        self.cairo_surface = None  # cached image as a cairo surface

    def image(self):
        return self.data
