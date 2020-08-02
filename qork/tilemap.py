#!/usr/bin/env python

import os, sys

from .util import BlockOutput

with BlockOutput():
    import pytmx

import PIL
from PIL import ImageOps

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
        # TODO: do correct filename
        tmx = self.tmx = pytmx.TiledMap("data/" + self.fn, image_loader=self._load_img)
        # print(tmx.layers)
        layer_ofs = 0
        for i, layer in enumerate(tmx.layers):
            if isinstance(layer, pytmx.TiledImageLayer):
                pass
            else:
                layer_props = layer.properties
                if 'depth' not in layer_props and 'dynamic' not in layer_props:
                    # STATIC: combine all tiles into giant image?
                    sz = ivec2(tmx.width * tmx.tilewidth, tmx.height * tmx.tileheight)
                    fullmap = Image.new(mode="RGBA", size=tuple(sz), color=(0,0,0,0))
                    for x, y, image in layer.tiles():
                        fullmap.paste(image, (int(x * tmx.tilewidth), int(y * tmx.tileheight)))
                    pos = vec3(
                        tmx.width/2 - 1/2,
                        -tmx.height/2 + 1/2,
                        layer_ofs
                    )
                    m = self.add(Mesh(image=fullmap, pos=pos, scale=vec3(tmx.width,tmx.height,1)))
                    m.material.texture.filter = (gl.NEAREST, gl.NEAREST)
                    # m.material.texture.anisotropy = 1.0 # def
                    m.material.texture.repeat_x = False
                    m.material.texture.repeat_y = False
                elif hasattr(layer, "tiles"):
                    pass
                    for x, y, image in layer.tiles():
                        if image:
                            pos = vec3(vec2(x, -y), layer_ofs)
                            m = self.add(Mesh(image=image, pos=pos))
                            m.material.texture.filter = (gl.NEAREST, gl.NEAREST)
                            # m.material.texture.anisotropy = 1.0 # def
                            m.material.texture.repeat_x = False
                            m.material.texture.repeat_y = False
                for obj in layer:
                    pass
            layer_ofs += 0.1

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

        newimg = not self.cache.has(fn)
        img = self.cache(fn)
        if newimg:
            img.data = img.data.convert("RGBA")
            data = img.data.getdata()
            d = []
            for e in data:
                if e[0:3] == (255, 0, 255):
                    d.append((0, 0, 0, 0))
                else:
                    d.append(e)

            img.data.putdata(d)
        # print(img.data.size)

        def loader(dim=None, flags=None):
            # TODO: cached cropped image
            if dim is None:
                return img
            key = fn + "+" + ",".join(map(lambda s: str(s), dim))
            # print(key)
            h, v, d = False, False, False
            if flags:
                h = flags.flipped_horizontally
                v = flags.flipped_vertically
                d = flags.flipped_diagonally
                if d or h or v:
                    if d:
                        key += 'd'
                    if h:
                        key += 'h'
                    if v:
                        key += 'v'
                    key = '+' + ''.join(sorted(key))
            r = self.app.cache.get(key, None)
            if r is None:
                # print(dim)
                region = [dim[0], dim[1], dim[0] + dim[2], dim[1] + dim[3]]
                r = img.data.crop(region)
                if h:
                    r = r.transpose(Image.FLIP_LEFT_RIGHT)
                if v:
                    r = r.transpose(Image.FLIP_TOP_BOTTOM)
                # if d:
                #     r.transpose(Image.ROTATE_180)
                # TODO: do flips
                self.app.cache[key] = r
            return r
            # print('loader', dim, flags)
            # return fn

        return loader
        # return self.cache(path)
