#!/usr/bn/env python
from .resource import *
from .util import *
from glm import ivec2, vec2
import cson
from PIL import Image
from copy import copy
from os import path
from .material import Material
from dataclasses import dataclass, field
from typing import Set
import weakref

# from dataclasses import dataclass


class Sprite(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.app
        fn = self.fn
        assert fn.lower().endswith(".cson")
        # data = None
        # for dp in self.app._data_paths:
        #     try:
        #         full_fn = path.join(dp, fn)
        #         with open(full_fn, "rb") as f:
        #             data = self.data = cson.load(f)
        #             self.full_fn = full_fn
        #             break
        #     except FileNotFoundError:
        #         pass
        # assert data
        self.full_fn = self.app.resource_path(fn)
        if self.full_fn is None:
            raise FileNotFoundError("Could not find sprite CSON for " + self.fn)
        with open(self.full_fn, "rb") as f:
            self.data = data = cson.load(f)
        assert data

        self.skins = data["skins"]
        # self.skin = 0
        size = data.get("size",None)
        self.size = ivec2(size) if size else None
        tile_size = data.get("size",None)
        self.tile_size = ivec2(tile_size) if tile_size else None
        origin = data.get("origin",None)
        self.origin = vec2(origin) if origin else None
        
        mask = data.get('mask', None)
        if mask:
            self.mask = vec2(mask)

        self.animation_meta = data["animation"]
        self.frames = self.animation_meta["frames"]
        self.speed = self.animation_meta.get("speed", 1.0)
        images = []
        self.layers = [[[]]]

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
                size = min(*sheet.size)

                # if size was not provided, approximate it
                if self.size is None:
                    self.size = ivec2(size)
                if self.tile_size is None:
                    self.tile_size = ivec2(size)
                if self.origin is None:
                    self.origin = size/2
                
                sheet = sheet.convert("RGBA")
            assert sheet
            if sheet_sz is None:
                sheet_sz = ivec2(sheet.size) / self.tile_size
                self.tile_count = tile_count = sheet_sz.x * sheet_sz.y

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

        # Process and store sequence flags (hflip, once)
        # This will generate flipped versions of tiles
        flipped_images = {}
        tile_id = Wrapper(tile_count)

        self.defaults = None

        def visit(seq, path):
            global frame_id
            i = 0
            hflip, vflip = False, False
            # print(seq, path)
            for tile in seq:
                if tile == "hflip" or tile == "+hflip":
                    hflip = True
                elif tile == "-hflip":
                    hflip = False
                elif tile == "vflip" or tile == "+vflip":
                    vflip = True
                elif tile == "-vflip":
                    vflip = False
                elif tile == "default":
                    name = path[-1]
                    if not name in self.flags:
                        self.flags[name] = SpriteFlags()
                    self.flags[name].default = True
                    data["default"] = path
                elif tile == "once":
                    name = path[-1]
                    if not name in self.flags:
                        self.flags[name] = SpriteFlags()
                    self.flags[name].once = True
                elif hflip:
                    if tile not in flipped_images:
                        for layer in self.layers:
                            for skin in layer:
                                img = skin[tile].copy()
                                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                                skin.append(img)
                        seq[i] = tile_id()  # change ID to modified version
                        flipped_images[tile] = tile_id()
                        tile_id.value += 1
                    else:
                        seq[i] = flipped_images[tile]
                i += 1
            # remove flags from sequence
            seq = filter(lambda x: not isinstance(x, str), seq)

        # if a certain sequence is marked default, then fill it in

        recursive_each(list, self.frames, visit)

        self.animation = SpriteAnimation(self)


class SpriteAnimation(Material):
    class Sequence:
        @dataclass
        class Entry:
            frame: int
            flags: set = field(default_factory=lambda: set())

        def __init__(self, name, tup, tup_ids, frames):
            self.name = name
            self.tup = tup
            self.tup_ids = tup_ids
            self.frames_meta = frames
            frames = list(filter(lambda x: not isinstance(x, str), frames))
            self.frames = frames = list(
                map(lambda x: SpriteAnimation.Sequence.Entry(x), frames)
            )
            # print('Sequence', name, tup, tup_ids, list(map(lambda x: x.frame, frames)))

    def __init__(self, sprite):
        # self.node = node
        self.app = sprite.app
        sprite = self.sprite = sprite
        data = self.data = sprite.data
        self.animation = data["animation"]
        self.speed = self.animation.get("speed", 1.0)
        self.frames = self.animation["frames"]
        self.speed = self.animation["speed"]
        self.categories = data["states"]
        self.category_name_to_id = {}
        for i, category in enumerate(self.categories):
            self.category_name_to_id[category] = i

        self.defaults_name = list(data["default"])
        # print(self.defaults_name)

        # this will be replaced with the IDs when we get those
        self.defaults = list(data["default"])

        self.default_frames = {}
        self.default_frames_name = {}
        self.possible_states = {}
        self.possible_states_name = {}
        self.state_frame_count = []

        state_stack = Wrapper([])

        self.sequences = {}  # id tuple -> Sequence
        self.sequences_name = {}  # name tuple -> Sequence

        # state names to state categories
        self.state_name_to_id = {}
        self.state_id_to_name = {}

        self.next_state_id = {}  # state id -> next state seq id

        # Recursive animation tree visitor function (called below)
        # Walks the sprite animation tree, creating stateful animation sequences
        def walk_anim_tree(frames, name, frame, depth=-1):

            if depth >= 0:
                # allow conversion between state names and ids

                # init next_state_id for this depth?
                # 'depth' ends up being the category id
                if depth not in self.next_state_id:
                    new_id = 0
                    self.next_state_id[depth] = 1
                else:
                    new_id = self.next_state_id[depth]
                    self.next_state_id[depth] += 1
                if depth not in self.state_id_to_name:
                    self.state_id_to_name[new_id] = name
                if name not in self.state_name_to_id:
                    self.state_name_to_id[name] = new_id

            if name:

                category = self.categories[depth]
                if depth not in self.default_frames:
                    # print(depth, name, type(frame), frame)
                    self.default_frames[depth] = name
                    self.default_frames_name[category] = name
                    self.possible_states[depth] = []
                    self.possible_states_name[category] = []
                    self.state_frame_count += [0]

                self.state_frame_count[depth] += 1
                self.possible_states[depth].append(name)
                self.possible_states_name[category].append(name)

            if type(frame) is dict:
                for k, v in frame.items():
                    state_stack(state_stack() + [k])
                    walk_anim_tree(frames, k, v, depth + 1)
                    state_stack(state_stack()[:-1])
            elif type(frame) is list:
                # print(tuple(state_stack()), '=', frame)
                state_stack_ids = []

                # ['alive', 'stand', 'walk'] -> [0,2,7]...
                for s in state_stack():
                    state_stack_ids.append(self.state_name_to_id[s])

                tup = tuple(state_stack())
                tup_ids = tuple(state_stack_ids)
                seq = SpriteAnimation.Sequence(name, tup_ids, tup, frame)
                # print(name, tup_ids, tup, frame)
                self.sequences[tup_ids] = seq
                self.sequences_name[tup] = seq

        # print(state_stack())
        walk_anim_tree(self.frames, "", self.frames)
        # print(self.sequences)

        for i, d in enumerate(self.defaults):
            self.defaults[i] = self.state_name_to_id[d]

        self.t = 0

    def get_sequence(self, states):
        # look up a sequence based on state tuple
        states = tuple(states)
        if not states:
            return []
        if states and isinstance(states[0], (int, float)):
            return self.sequences[states]
        else:
            return self.sequences_name[states]

    # def update(self, dt):
    #     self.t += dt * 2
    #     self.frame = int(self.t % 12)
    #     pass

    # def use(self, idx):
    #     pass


class SpriteMaterial(Material):
    def __init__(self, sprite, sync=True):
        super().__init__(None)
        self._sprite = weakref.ref(sprite)
        animation = sprite.animation
        self.skin = 0
        self.frame = 0  # changed through update()
        self.states = list(animation.defaults)
        # self.frames_tup = tuple()
        self.t = 0
        self.sync = sync  # sync material states with sprite states
        # if sync:
        # TODO: node.state['blah'].change(...
        self.sequence = sprite.animation.get_sequence(self.states)

    @property
    def sprite(self):
        return self._sprite()

    @property
    def animation(self):
        return self.sprite.animation

    def update(self, dt):
        anim = self.animation
        self.t += dt * anim.speed
        if self.sequence:
            idx = int(self.t) % len(self.sequence.frames)
            self.frame = self.sequence.frames[idx].frame

    def state(self, category, state=DUMMY):
        sprite = self.sprite

        if type(category) is str:
            # use id instead of string
            category = sprite.animation.category_name_to_id[category]

        if state is DUMMY:
            return self.states[category]  # GET

        if type(state) is str:
            state = sprite.animation.state_name_to_id[state]

        s = self.states[category]

        if s != state:
            self.states[category] = state
            # renew sequence

            # TEMP: we don't have state wildcards yet, so we'll repeatedly pop
            #   from the back of the states to allow for unnested partial
            #   or single categories.  For example:
            #         assuming ('alive','walk','left') is valid
            #         and ('dead',) is valid
            #         if ('dead','walk','left') and ('dead','walk') is invalid,
            #             it will collapse twice down to ('dead',)
            # In the future, we may use ('dead', '*', '*') to signify this
            states = self.states
            seq = None
            while states:
                seq = sprite.animation.get_sequence(self.states)
                if seq:
                    break
                states = states[-1]  # pop
            if seq is None or not states:
                raise Exception("no such state: ", category, "=", state)
            self.sequence = seq
            # self.t = 0

    def use(self, idx=0):
        # TODO: look up frame
        frame = self.frame
        sprite = self.sprite
        if not sprite or frame == -1:
            return False
        for i in range(len(sprite.layers)):
            sprite.layers[i][self.skin][frame].use(i)
        return True
