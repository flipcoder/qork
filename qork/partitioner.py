#!/usr/bin/python

import enum
from collections import defaultdict
from .signal import Signal, Container


class Partitioner:
    CollisionRef = enum.Enum("Ref", "ref type name")
    CollisionEvent = enum.Enum("Event", "overlap exclusive enter leave")

    def __init__(self, app):

        self.app = app

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

    def collisions(self, dt):
        """
        Do collision checks.  This is horribly unoptimized but it works for now
            with the correct interface.
        """

        if not self.overlap:
            return

        scene = self.app.scene
        with scene:

            for a in scene.walk():
                # only check if a is solid
                # if not a.solid:
                #     continue

                if a.world_box is None:
                    continue

                # for each slot, loop through each slot
                for b in scene.walk():
                    # only check if b is solid
                    # if not b.solid:
                    #     continue
                    if a is not b:
                        if b.world_box is None:
                            continue

                        aa = a.world_box
                        bb = b.world_box

                        col = not (
                            bb[0].x > aa[1].x
                            or bb[1].x < aa[0].x
                            or bb[0].y > aa[1].y
                            or bb[1].y < aa[0].y
                            or bb[0].z > aa[1].z
                            or bb[1].z < aa[0].z
                        )
                        if col:
                            ta = type(a)
                            tb = type(b)
                            an = a.name
                            bn = a.name

                            # TODO: obviously make this more efficient

                            # instance
                            if self.overlap[a][b](a, b, dt):
                                break
                            if self.overlap[b][a](b, a, dt):
                                break

                            # names
                            if an or bn:
                                if self.overlap[a][bn](a, b, dt):
                                    break
                                if self.overlap[b][an](b, a, dt):
                                    break
                                if self.overlap[an][b](a, b, dt):
                                    break
                                if self.overlap[bn][a](b, a, dt):
                                    break
                                if self.overlap[an][bn](a, b, dt):
                                    break
                                if an != bn:
                                    if self.overlap[bn][an](b, a, dt):
                                        break

                            # types
                            if self.overlap[a][tb](a, b, dt):
                                break
                            if self.overlap[b][ta](b, a, dt):
                                break
                            if self.overlap[ta][b](a, b, dt):
                                break
                            if self.overlap[tb][a](b, a, dt):
                                brea
                            if self.overlap[ta][tb](a, b, dt):
                                break
                            if ta is not tb:
                                if self.overlap[tb][ta](b, a, dt):
                                    break
