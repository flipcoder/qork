#!/usr/bin/python

import enum
from collections import defaultdict
from .signal import Signal, Container


class Partitioner:
    CollisionRef = enum.Enum("Ref", "ref type name")
    CollisionEvent = enum.Enum("Event", "overlap exclusive enter leave")

    def __init__(self, scene):

        # self.app = app
        self.scene = scene

        # reftype -> (a, b) -> action
        # self.signals = [defaultdict(lambda: defaultdict(Signal)) for x in range(RefType)]

        # self.nodes = [[] for x in range(RefType)]

        self.overlap = defaultdict(lambda: defaultdict(Signal))

    def __iadd__(self, node):
        return self

    def __isub__(self, node):
        return self

    def update(self, dt):
        self.collisions(dt)

    def refresh(self):
        pass

    def register_node(self):
        pass

    #     scene = self.app.scene
    #     with scene:
    #         for a in self.scene.walk():
    #             ta = type(a)
    #             for pairs in self.signals[RefType.type]:
    #                 if ta in pairs:
    #                     # self.nodes
    #             # p0 = pairs[0]
    #             # if type(p0) is weakref.ref:
    #             #     p0 = p0()
    #             #     if p0 == a:
    #             #         # add obj to every pair
    #             # if type(a) in pairs:
    #             #     cbs = self.overlap[RefType.type]
    #             #     for cbpair in cbs:

    #                 # if a.name in pairs:
    #                 #     pairs =
    #             # if ta in self.solid_types:
    #             #     self.types[ta] += a
    #             # if ta in self.solid_names:
    #             #     self.names[ta] += a

    #     self.initial_refresh = True

    @staticmethod
    def collision(aa, bb):
        """
        Manually check collision between 2 objects.
        Will not fire any collision signals.
        """
        return aa.world_box.overlap(bb.world_box)

    def collisions(self, dt):
        """
        Do collision checks.  This is horribly unoptimized but it works for now
            with the correct interface.
        """

        if not self.overlap:
            return

        scene = self.scene
        with scene:

            for a in scene.walk_fast():
                if a.world_box is None:
                    continue

                # for each slot, loop through each slot
                for b in scene.walk_fast():
                    if a is not b:
                        if b.world_box is None:
                            continue

                        if self.collision(a, b):
                            ta = type(a)
                            tb = type(b)
                            an = a.name
                            bn = a.name

                            # TODO: obviously make this more efficient

                            # instance
                            if self.overlap[a][b](a, b, dt):
                                continue
                            if self.overlap[b][a](b, a, dt):
                                continue

                            # names
                            if an or bn:
                                if self.overlap[a][bn](a, b, dt):
                                    continue
                                if self.overlap[b][an](b, a, dt):
                                    continue
                                if self.overlap[an][b](a, b, dt):
                                    continue
                                if self.overlap[bn][a](b, a, dt):
                                    continue
                                if self.overlap[an][bn](a, b, dt):
                                    continue
                                if an != bn:
                                    if self.overlap[bn][an](b, a, dt):
                                        continue

                            # types
                            if self.overlap[a][tb](a, b, dt):
                                continue
                            if self.overlap[b][ta](b, a, dt):
                                continue
                            if self.overlap[ta][b](a, b, dt):
                                continue
                            if self.overlap[tb][a](b, a, dt):
                                brea
                            if self.overlap[ta][tb](a, b, dt):
                                continue
                            if ta is not tb:
                                if self.overlap[tb][ta](b, a, dt):
                                    continue
