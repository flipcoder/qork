#!/usr/bin/python

from collections import defaultdict
from .signal import Signal


class Partitioner:
    def __init__(self):

        self.overlap = defaultdict(lambda: defaultdict(Signal))

    def update(self, dt):

        # TODO: only check collisions on world root

        with self.world:

            for a in self.world.__iter__(recursive=True):
                # only check if a is solid
                if not a:
                    continue

                if a.world_box is None:
                    continue

                # for each slot, loop through each slot
                for b in self.world.__iter__(recursive=True):
                    # only check if b is solid
                    if not b:
                        continue
                    if a is not b:
                        if b.world_box is None:
                            continue

                        col = not (
                            b.world_box[0].x > a.world_box[1].x
                            or b.world_box[1].x < a.world_box[0].x
                            or b.world_box[0].y > a.world_box[1].y
                            or b.world_box[1].y < a.world_box[0].y
                            or b.world_box[0].z > a.world_box[1].z
                            or b.world_box[1].z < a.world_box[0].z
                        )
                        if col:
                            self.overlap[a][b](a, b, dt)
                            self.overlap[b][a](b, a, dt)
