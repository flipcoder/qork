#!/usr/bin/env python
import numpy as np
from .resource import *
from glm import ivec2, vec2
import cson
from PIL import Image

class Sprite(Resource):
    def __init__(self, app, fn, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        
