#!/usr/bin/python


class Partitioner:
    def __init__(self):
        self.overlap = {}  # (a,b) -> signal

    def update(self, dt):

        # TODO: only check collisions on world root

        with self.world:

            for a in self.world.children:
                # only check if a is solid
                if not a:
                    continue

                if a.box is None:
                    continue

                # for each slot, loop through each slot
                for b in self.world.children:
                    # only check if b is solid
                    if not b:
                        continue
                    if a is not b:
                        if b.box is None:
                            continue

                        col = not (
                            b.min.x > a.max.x
                            or b.max.x < a.min.x
                            or b.min.y > a.max.y
                            or b.max.y < a.min.y
                            or b.min.z > a.max.z
                            or b.max.z < a.min.z
                        )
                        if col:
                            try:
                                self.overlap[a][b](a, b, dt)
                            except KeyError:
                                pass
                            try:
                                self.overlap[b][a](b, a, dt)
                            except KeyError:
                                pass
