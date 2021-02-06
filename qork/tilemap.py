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
    collision_handler = True

    class Layer:
        def __init__(self):
            self.pages = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.layers = Container()
        # TODO: do correct filename
        if self.fn is None:
            self.full_fn = None
            # Empty tilemap
            return

        self.load(self.fn, **kwargs)

        self.layers = []

    def load(self, fn=None, **kwargs):
        """Load tilemap using filename"""

        # use filename
        if fn is not None:
            self.fn = fn

        self.full_fn = self.app.resource_path(self.fn, throw=True)
        tmx = self.tmx = pytmx.TiledMap(self.full_fn, image_loader=self._load_img)
        self.local_box = Box((0, 0, -100), (tmx.width, tmx.height, 100))  # tmp
        # print('lb', self.local_box)
        # print('wb', self.world_box)

        rules = kwargs.get("rules", {})
        # print(tmx.layers)
        layer_ofs = 0.0
        # tmx.layers = sorted(tmx.layers)
        def get_id(layer):
            try:
                return layer.id
            except AttributeError:
                return 0

        layers = sorted(tmx.layers, key=get_id)
        # for i, layer in enumerate(tmx.layers):
        decal_layer_skip = 0
        popup = kwargs.get("popup", False)
        decal_offset = kwargs.get("decal_offset", 0.001)
        group_offset = kwargs.get("group_offset", 1.0)

        # let's break the map into pages
        page = ivec2(8)  # page size

        last_group = None
        group = None
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
                last_group = group
                group = layer_props.get("group", None)
                if group != last_group:
                    layer_ofs += group_offset
                    last_group = group
                layer_node = self.add(Node(layer.name))
                page_node = layer_node.add(Node("page"))

                # calculate which layers can be combined (decals)
                j = i + 1
                while j < len(layers):
                    if isinstance(layers[j], pytmx.TiledTileLayer):
                        dgroup = layers[j].properties.get("group", None)
                        if (
                            "decal" in layers[j].name.lower()
                            or "decal" in layers[j].properties
                            or (dgroup != None and group != None and dgroup == group)
                        ):
                            depth = layer_props.get("depth", "default")
                            ddepth = layers[j].properties.get("depth", "default")
                            # if same group but diff depth val, don't do decal
                            if (
                                depth is not None
                                and ddepth is not None
                                and depth == ddepth
                            ):
                                decal_layers.append(layers[j])
                                decal_layer_skip += 1
                            else:
                                break
                        else:
                            break
                    j += 1

                if hasattr(layer, "tiles"):
                    # if layer_props.get("dynamic", 0) != 1:
                    try:
                        depth = layer_props["depth"]
                        depth = True
                        # print(layer.name, 'has depth')
                    except KeyError:
                        depth = False

                    # The check to determine if tile layer is static
                    # In popup mode, tiles with 'depth' need to pop out
                    if not depth:
                        # FLAT STATIC: combine all layer tiles into giant image page
                        sz = ivec2(
                            tmx.width * tmx.tilewidth, tmx.height * tmx.tileheight
                        )
                        fullmap = Image.new(
                            mode="RGBA", size=tuple(sz), color=(0, 0, 0, 0)
                        )
                        for x, y, image in layer.tiles():
                            fullmap.paste(
                                image,
                                (int(x * tmx.tilewidth), int(y * tmx.tileheight)),
                                image,
                            )
                        for decal_layer in decal_layers:
                            for x, y, decal in decal_layer.tiles():
                                fullmap.paste(
                                    decal,
                                    (int(x * tmx.tilewidth), int(y * tmx.tileheight)),
                                    decal,
                                )
                        pos = vec3(
                            tmx.width / 2 - 1 / 2,
                            -tmx.height / 2 + 1 / 2 - (layer_ofs if popup else 0),
                            layer_ofs,
                        )
                        m = page_node.add(
                            Mesh(
                                image=fullmap,
                                pos=pos,
                                scale=vec3(tmx.width, tmx.height, 1),
                            )
                        )
                        m.material.filter(False)
                        m.material.repeat(False)
                        # else:
                        #     # DEPTH: depth buffered against objects, generate one combined layer mesh
                        #     pass
                    else:
                        # DYNAMIC: generate depth tiles (slow rendering!)
                        # for x, y, tile in layer.tiles():
                        for y in range(tmx.height):
                            for x in range(tmx.width):
                                images = 0
                                tile = tmx.images[layer.data[y][x]]

                                image = None

                                def make_image():
                                    return Image.new(
                                        mode="RGBA",
                                        size=(tmx.tilewidth, tmx.tileheight),
                                        color=(0, 0, 0, 0),
                                    )

                                if tile:
                                    if not images:
                                        image = make_image()
                                    image.paste(tile, (0, 0), tile)
                                    images += 1

                                decal = None
                                for decal_layer in decal_layers:
                                    decal = tmx.images[decal_layer.data[y][x]]
                                    if decal:
                                        if not images:
                                            image = make_image()
                                        image.paste(decal, (0, 0), decal)
                                        images += 1

                                if images:
                                    pos = vec3(
                                        vec2(x, -y - (layer_ofs if popup else 0)),
                                        layer_ofs,
                                    )
                                    m = page_node.add(Mesh(image=image, pos=pos))

                                    if popup:
                                        m.rotate(0.25, X)
                                        m.z += 1 / 2
                                        m.y -= 1 / 2
                                    m.material.filter(False)
                                    m.material.repeat(False)

                                del image
                else:
                    # TILED OBJECTS
                    for obj in layer:
                        pos = vec3(
                            vec2(
                                obj.x / tmx.tilewidth,
                                -obj.y / tmx.tileheight - (layer_ofs if popup else 0),
                            ),
                            layer_ofs,
                        )
                        m = page_node.add(
                            Mesh(obj.name or "", image=obj.image, pos=pos)
                        )
                        if popup and "depth" in layer.properties:
                            m.rotate(0.25, X)
                            m.z += 1 / 2
                            m.y -= 1 / 2
                        m.material.filter(False)
                        m.material.repeat(False)
                page_node.frozen = True
                page_node.frozen_children = True
                layer_ofs += decal_offset

            # TODO: combine all dynamic kobjects of similar texture

            # if last_group is not None and last_group != group:
            #     print(group)
            #     layer_ofs += 1.0
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

    def handle_collision(self, other):
        wb = other.world_box
        # TODO: get the range of tiles that are inside wb
        # TODO: check collision against their collision masks
        return True

