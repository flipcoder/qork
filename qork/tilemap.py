#!/usr/bin/env python

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
        self.layers = Container()

        # TODO: load tmx

