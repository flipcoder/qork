#!/usr/bin/env python

import os, sys

from .util import BlockOutput

with BlockOutput():
    import pytmx

import PIL

from .node import *
from .mesh import *

# class TileMapTile:
#     pass

# class TilesetTile(Node):
#     pass

# class TileMapLayer(Node):
#     def __init__(self, *args, **kwargs):
#         pass

# class TileMapLayerGroup(Node):
#     def __init__(self, *args, **kwargs):
#         pass


class TileMap(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.layers = Container()
        tmx = self.tmx = pytmx.TiledMap(self.fn, image_loader=self._load_img)
        # print(tmx.layers)
        for i, layer in enumerate(tmx.layers):
            if isinstance(layer, pytmx.TiledImageLayer):
                pass
            else:
                if hasattr(layer, "tiles"):
                    for x, y, image in layer.tiles():
                        if image:
                            pos = vec3(vec2(x, y), 0)
                            # TODO: cache shape too
                            # print('try to add')
                            m = self.add(Mesh(image, pos=pos, scale=0.1, name="Tile"))
                            print(m.tree())
                for obj in layer:
                    pass
                    # print(obj)

    def _load_img(self, fn, colorkey, tileset=None):

        # print(fn, colorkey, tileset)
        # # print('!!!!!!!!')
        # img = None
        # for dp in self.app._data_paths:
        #     # TODO: cache
        #     try:
        #         img = PIL.Image.open(os.path.join(dp, fn))
        #     except FileNotFoundError:
        #         continue
        #     if img:
        #         break
        # if not img:
        #     raise FileNotFoundError()
        # img = img.convert("RGBA")

        img = self.cache(fn)
        # print(img.data.size)

        def loader(dim=None, flags=None):
            # TODO: cached cropped image
            if dim is None:
                return img
            key = fn + "+" + ",".join(map(lambda s: str(s), dim))
            h, v = False, False
            if flags:
                h = flags.flipped_horizontally
                v = flags.flipped_vertically
                if h and v:
                    key += "+hv"
                elif h:
                    key += "+h"
                elif v:
                    key += "+v"
            r = self.app.cache.get(key, None)
            if r is None:
                region = [dim[0], dim[1], dim[0] + dim[2], dim[1] + dim[3]]
                r = img.data.crop(region)
                # TODO: do flips
                self.app.cache[key] = r
            # print(key, "->", r)
            return r
            # print('loader', dim, flags)
            # return fn

        return loader
        # return self.cache(path)
