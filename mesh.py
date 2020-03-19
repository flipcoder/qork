#!/usr/bin/env python
from node import *
import numpy as np
from PIL import Image
import moderngl as gl
from defs import *
import cson
from glm import ivec2, vec2

class Sprite:
    def __init__(self, fn):
        assert fn.lower().endswith('.cson')
        with open(fn, 'rb') as f:
            data = self.data = cson.load(f)
        
        self.skins = data['skins']
        self.skin = 0
        self.tile_size = ivec2(data['tile_size'])
        self.size = ivec2(data['size'])
        self.origin = vec2(data['origin'])
        self.mask = vec2(data['mask'])
        
        self.animation = data['animation']
        self.frames = self.animation['frames']
        self.speed = self.animation['speed']
        self.layers = []
        self.frame = 0

        images = []
        self.layers = [[[]]]
        
        sheet_sz = None
        skin_id = 0
        for skin in data['skins']:
            sheet = Image.open('data/' + skin).convert('RGBA')
            if sheet_sz == None:
                sheet_sz = ivec2(sheet.size)/self.tile_size
                        
            for i in range((sheet_sz.x * sheet_sz.y)):
                # crop frame from spritesheet
                x = (i % sheet_sz.x) * self.tile_size.x
                y = (i //sheet_sz.x) * self.tile_size.y
                l = x + self.tile_size.x
                b = y + self.tile_size.y
                img = sheet.crop((x,y,l,b))
                # replace pink pixels with transparency
                pixels = np.array(img)
                for x in range(len(pixels)):
                    for y in range(len(pixels[x])):
                        if pixels[x][y][0] == 255 and \
                            pixels[x][y][1] == 0 and \
                            pixels[x][y][2] == 255:
                            pixels[x][y][3] = 0
                img = Image.fromarray(pixels)
                images.append(img)
            
            self.layers[0][skin_id] = images
            skin_id += 1
        
    def logic(self, t):
        pass

class Mesh(Node):
    def __init__(self, app, fn=None, **kwargs):
        super().__init__(app, **kwargs)
        self.vertices = None
        self.layers = [] # layers -> skins -> images
        self.fn = fn
        self.skin = 0
        self.sprite = None # frame data here if mesh is a sprite
        self.image = None
        self.frame = 0
    def get_frame(self):
        return self.sprite.frame if self.sprite else self.frame
    def load(self, fn=None):
        fn = self.fn = fn or self.fn # use either filename from ctor or arg

        # json = sprite data
        if fn and fn.lower().endswith('.cson'):
            self.sprite = Sprite(fn)
            self.layers = self.sprite.layers
            if not self.layers or not self.sprite:
                assert False # failed to load
            # self.scale(self.sprite['size'])
        else: # not sprite
            if isinstance(fn, str):
                fn = [fn]
            if not self.image: # mesh image not preloaded?
                self.layers = self.layers or [[[]]] # layers -> skins -> images
                for img in fn:
                    # [0][0] = default layer and skin (image list)
                    self.layers[0][0].append(Image.open(img).convert('RGBA'))
        for layer in self.layers:
            for skin in layer:
                for i in range(len(skin)): # for img in skin:
                    img = skin[i]
                    # print(img.size)
                    skin[i] = self.ctx.texture(img.size, 4, img.tobytes())
        assert type(self.vertices) == np.ndarray # mesh has geometry?
        self.vbo = self.ctx.buffer(self.vertices.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.app.shader, self.vbo, 'in_vert', 'in_text')
    def logic(self, t):
        super().logic(t)
        if self.sprite:
            self.sprite.logic(t)
    def render(self):
        if self.visible:
            self.app.shader['Model'] = flatten(self.matrix(WORLD))
            for i in range(len(self.layers)):
                self.layers[i][self.skin][self.get_frame()].use(i)
            self.vao.render(self.mesh_type)
        super().render()

