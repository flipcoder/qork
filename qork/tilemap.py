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
        rules = kwargs.get("rules", {})
        # print(tmx.layers)
        layer_ofs = 0
        # tmx.layers = sorted(tmx.layers)
        layers = sorted(tmx.layers, key=lambda x: x.id)
        # for i, layer in enumerate(tmx.layers):
        decal_layer_skip = 0
        
        # let's page the map in pages
        page = ivec2(8) # page size
        
        for i, layer in enumerate(layers):
            # print(layer.id)
            if isinstance(layer, pytmx.TiledImageLayer):
                pass
            elif isinstance(layer, pytmx.TiledTileLayer):

                # skip previously processed decal layers
                if decal_layer_skip:
                    decal_layer_skip -= 1
                    # print(layer.name,'is decal')
                    continue

                decal_layers = []
                layer_props = layer.properties
                group = layer_props.get('group', '')
                layer_node = self.add(Node(layer.name))
                page_node = layer_node.add(Node("page"))

                # calculate which layers can be combined (decals)
                j = i+1
                while j < len(layers):
                    if isinstance(layers[j], pytmx.TiledTileLayer):
                        dgroup = layers[j].properties.get('group', None)
                        if 'decal' in layers[j].name.lower() or \
                            'decal' in layers[j].properties or \
                            (dgroup!=None and group!=None and dgroup == group) \
                        :
                            depth = layer_props.get('depth', 'default')
                            ddepth = layers[j].properties.get('depth', 'default')
                            # if same group but diff depth val, don't do decal
                            if depth is not None and ddepth is not None and depth == ddepth:
                                decal_layers.append(layers[j])
                                decal_layer_skip += 1
                        else:
                            break
                    j += 1
                
                if hasattr(layer, "tiles"):
                    if layer_props.get("dynamic", 0) != 1:
                        # STATIC
                        # if layer_props.get('depth',0) != 1:
                        # FLAT STATIC: combine all layer tiles into giant image
                        sz = ivec2(
                            tmx.width * tmx.tilewidth, tmx.height * tmx.tileheight
                        )
                        fullmap = Image.new(
                            mode="RGBA", size=tuple(sz), color=(0, 0, 0, 0)
                        )
                        for x, y, image in layer.tiles():
                            fullmap.paste(
                                image, (int(x * tmx.tilewidth), int(y * tmx.tileheight)), image
                            )
                        for decal_layer in decal_layers:
                            for x, y, decal in decal_layer.tiles():
                                fullmap.paste(
                                    decal, (int(x * tmx.tilewidth), int(y * tmx.tileheight)), decal
                                )
                        pos = vec3(
                            tmx.width / 2 - 1 / 2, -tmx.height / 2 + 1 / 2, layer_ofs
                        )
                        m = page_node.add(
                            Mesh(
                                image=fullmap,
                                pos=pos,
                                scale=vec3(tmx.width, tmx.height, 1),
                            )
                        )
                        m.material.texture.filter = (gl.NEAREST, gl.NEAREST)
                        m.material.texture.repeat_x = False
                        m.material.texture.repeat_y = False
                        # else:
                        #     # DEPTH: depth buffered against objects, generate one combined layer mesh
                        #     pass
                    else:
                        # DYNAMIC: generate dynamic tiles (slow rendering!)
                        for x, y, image in layer.tiles():
                            if image:
                                pos = vec3(vec2(x, -y), layer_ofs)
                                m = page_node.add(Mesh(image=image, pos=pos))
                                m.material.texture.filter = (gl.NEAREST, gl.NEAREST)
                                m.material.texture.repeat_x = False
                                m.material.texture.repeat_y = False
                else:
                    # TILED OBJECTS
                    for obj in layer:
                        pos = vec3(
                            vec2(
                                obj.x / tmx.tilewidth,
                                -obj.y / tmx.tileheight
                            ),
                            layer_ofs,
                        )
                        m = page_node.add(
                            Mesh(obj.name or "", image=obj.image, pos=pos)
                        )
                        m.material.texture.filter = (gl.NEAREST, gl.NEAREST)
                        m.material.texture.repeat_x = False
                        m.material.texture.repeat_y = False
                page_node.freeze = True
                page_node.freeze_children = True
                layer_ofs += 0.1
            # elif type(layer) is tuple:
            #     print(layer)

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
                        key += "d"
                    if h:
                        key += "h"
                    if v:
                        key += "v"
                    key = "+" + "".join(sorted(key))
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
