#!/usr/bin/env python
from .resource import *
from .util import *
from glm import ivec2, vec2
import cson
from PIL import Image
from copy import copy
from os import path

# from dataclasses import dataclass


class Sprite(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.app
        fn = self.fn
        assert fn.lower().endswith(".cson")
        data = None
        for dp in self.app._data_paths:
            try:
                full_fn = path.join(dp, fn)
                with open(full_fn, "rb") as f:
                    data = self.data = cson.load(f)
                    self.full_fn = full_fn
                    break
            except FileNotFoundError:
                pass
        assert data
        self.skins = data["skins"]
        self.skin = 0
        self.tile_size = ivec2(data["tile_size"])
        self.size = ivec2(data["size"])
        self.origin = vec2(data["origin"])
        self.mask = vec2(data["mask"])

        self.animation = data["animation"]
        self.frames = self.animation["frames"]
        self.speed = self.animation["speed"]
        images = []
        self.layers = [[[]]]
        self.extra = []  # extra generated images, like hflip

        # @dataclass
        # class SpriteFlags:
        #     once: bool = False
        class SpriteFlags:
            pass

        self.flags = {}

        sheet_sz = None
        skin_id = 0
        for skin in data["skins"]:
            sheet = None
            for dp in self.app._data_paths:
                try:
                    sheet = Image.open(path.join(dp, skin))
                except FileNotFoundError:
                    continue
                sheet = sheet.convert("RGBA")
            assert sheet
            if sheet_sz is None:
                sheet_sz = ivec2(sheet.size) / self.tile_size
                tile_count = sheet_sz.x * sheet_sz.y

            for i in range(tile_count):
                # crop frame from spritesheet
                x = (i % sheet_sz.x) * self.tile_size.x
                y = (i // sheet_sz.x) * self.tile_size.y
                L = x + self.tile_size.x
                b = y + self.tile_size.y
                img = sheet.crop((x, y, L, b))
                # replace pink pixels with transparency
                px = img.load()
                for y in range(img.height):
                    for x in range(img.width):
                        if px[x, y] == (255, 0, 255, 255):
                            px[x, y] = (0, 0, 0, 0)
                # img = Image.fromarray(pixels)
                images.append(img)
            self.layers[0][skin_id] = images
            skin_id += 1

        # process sequence flags (hflip, once)
        # hflip_imgs = {}
        # tile_id = Wrapper(tile_count)
        # def visit(seq, path):
        #     global frame_id
        #     i = 0
        #     hflip = False
        #     for tile in seq:
        #         if tile == 'hflip' or tile=='+hflip':
        #             hflip = True
        #         elif tile == '-hflip':
        #             hflip = False
        #         elif tile == 'once':
        #             name = path[-1]
        #             if not name in self.flags:
        #                 self.flags[name] = SpriteFlags()
        #             self.flags[name].once = True
        #         elif hflip:
        #             if tile not in hflip_imgs:
        #                 print(tile)
        #                 for layer in self.layers:
        #                     for skin in layer:
        #                         img = skin[tile].copy()
        #                         img.transpose(Image.FLIP_LEFT_RIGHT)
        #                         skin.append(tile_id())
        #                 print('new tile: ', tile_id())
        #                 seq[i] = tile_id() # change ID to modified version
        #                 hflip_imgs[tile] = tile_id()
        #                 tile_id.value += 1
        #             else:
        #                 seq[i] = hflip_imgs[tile]
        #         i += 1
        #     # remove flags from sequence
        #     seq = filter(lambda x: not isinstance(x, str), seq)
        # recursive_each(list, self.frames, visit)
