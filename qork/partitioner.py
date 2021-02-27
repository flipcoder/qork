#!/usr/bin/python

import enum
import weakref
from collections import defaultdict
from .signal import Signal, Container
from .node import Node


class Partitioner:
    CollisionRef = enum.Enum("Ref", "ref type name")
    CollisionEvent = enum.Enum("Event", "overlap apart enter leave")

    class NodeRef:
        def __init__(self, node):
            self.id = id(node)
            self.node = weakref.ref(node)
            # TODO: track usages

    class CollisionPair:
        def __init__(self, a, b, touching):
            self.objs = [
                weakref.ref(a),
                weakref.ref(b)
            ]
            self.touching = touching
    
    def __init__(self, scene):

        # self.app = app
        self.scene = scene

        # reftype -> (a, b) -> action
        # self.signals = [defaultdict(lambda: defaultdict(Signal)) for x in range(RefType)]

        # self.nodes = [[] for x in range(RefType)]

        self.overlap = defaultdict(lambda: defaultdict(Signal))
        self.apart = defaultdict(lambda: defaultdict(Signal))
        self.enter = defaultdict(lambda: defaultdict(Signal))
        self.leave = defaultdict(lambda: defaultdict(Signal))

        # self.watched_types_count = {}
        # self.watched_names_count = {}

        self.touched_this_frame = set()
        self.touched_last_frame = set()
        self.collision_pairs = {}

        self.id_to_noderef = {}

        # name -> signal dictionary
        self.sig_by_name = {
            'overlap': self.overlap,
            # 'apart': self.apart,
            'enter': self.enter,
            'leave': self.leave,
        }

    def sig(self, name):
        return self.sig_by_name[name]

    @property
    def collisions(self):
        return self.overlap or self.apart or self.enter or self.leave

    def __iadd__(self, node):
        self.register_node(node)
        return self

    def __isub__(self, node):
        self.unregister_node(node)
        return self

    def update(self, dt):
        self.collisions_update(dt)

    def refresh(self):
        pass

    def register_node(self, node):
        pass
    
    def unregister_node(self, node):
        if node.frozen:
            return

        # remove all node refs, which are created by collision registration
        node_id = id(node)
        try:
            noderef = self.id_to_noderef[node_id]
        except KeyError:
            # not referenced by partitioner
            return
        # TODO: remove usages
        del self.id_to_noderef[node_id]

    def register_callback(self, event, a, b, func):
        a_id, b_id = id(a), id(b)
        self.id_to_noderef[a_id] = a_ref = self.NodeRef(a)
        self.id_to_noderef[b_id] = b_ref = self.NodeRef(b)
        self.sig(event)[a_id][b_id] += func
        return True
    
    def unregister_callbacks(self, event, a, b=None):
        a_id, b_id = id(a), id(b)
        if b is None:
            del self.id_to_noderef[a]
            del self.sig(event)[a_id]
        else:
            del self.sig(event)[a_id][b_id]
            del self.sig(event)[b_id][a_id]
    
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

    def _sig(self, sig, a_in, b_in, a_out, b_out, dt):
        """Call a signal table with the params"""
        cb = sig[a_in][b_in]
        if cb:
            return cb(a_out, b_out, dt)

    def _run_callbacks(self, sig, a, b, dt):
        """Run all the callback comnbiations for an associated collsion table (overlap, enter, etc.)"""
        if not sig:
            return

        sigfunc = self._sig

        a_id, b_id = id(a), id(b)

        if sigfunc(sig, a_id, b_id, a, b, dt):
            return
        if sigfunc(sig, b_id, a_id, b, a, dt):
            return
        
        ta = type(a)
        tb = type(b)
        an = a.name
        bn = a.name
        check_types = ta is not Node and tb is not Node
        check_names = an or bn

        # name-to-instance collision
        if check_names:
            if an:
                # if sigfunc(sig, b_id, an, b, a, dt):
                #     return
                if sigfunc(sig, an, b_id, a, b, dt):
                    return
            if bn:
                if sigfunc(sig, a_id, bn, a, b, dt):
                    return
                # if sigfunc(sig, bn, a_id, b, a, dt):
                #     return
            if an and bn:
                if sigfunc(sig, an, bn, a, b, dt):
                    return
                # if an != bn:
                # if sigfunc(sig, bn, an, b, a, dt):
                #     return

        # type-to-type and instance-to-type collision
        if check_types:
            if sigfunc(sig, a_id, tb, a, b, dt):
                return
            # if sigfunc(sig, b_id, ta, b, a, dt):
            #     return
            if sigfunc(sig, ta, b_id, a, b, dt):
                return
            # if sigfunc(sig, tb, a_id, b, a, dt):
            #     return
            if sigfunc(sig, ta, tb, a, b, dt):
                return
            # if ta is not tb:
            # if sigfunc(sig, tb, ta, b, a, dt):
            #     return

        # name-to-type collision
        if check_names and check_types:
            if an:
                if sigfunc(sig, an, tb, a, b, dt):
                    return
                # if sigfunc(sig, tb, an, b, a, dt):
                #     return
            if bn:
                if sigfunc(sig, ta, bn, a, b, dt):
                    return
                # if sigfunc(sig, bn, ta, b, a, dt):
                #     return

    def collisions_update(self, dt):
        """
        Do collision checks.  This is horribly unoptimized but it works for now
            with the correct interface.
        """

        if not self.collisions:
            return

        # reset all pair touch states
        # for pair in self.touching:
        #     pair.touched = False
        # self.touching.clear()

        scene = self.scene
        with scene:

            for a in scene.walk_fast(): # ignores frozen elements
                if a.world_box is None:
                    continue

                # for each slot, loop through each slot
                for b in scene.walk_fast(): # ignores frozen elements
                    if a is not b:
                        if b.world_box is None:
                            continue
                        
                        col = self.collision(a, b)
                        if col:
                            ta = type(a)
                            tb = type(b)
                            an = a.name
                            bn = a.name

                            # collision pair enters a collision
                            if id(a) < id(b):
                                abkey = [a,b]
                                abkey = tuple(map(lambda x: id(x), abkey))
                                pair = self.collision_pairs.get(abkey, None)
                                if not pair:
                                    pair = self.collision_pairs[abkey] = Partitioner.CollisionPair(a,b,False)
                                if not pair.touching:
                                    pair.touching = True
                                    self.touched_this_frame.add(pair) # reset touch state next frame
                                    self._run_callbacks(self.enter, a, b, dt)
                                
                            self._run_callbacks(self.overlap, a, b, dt)

        # objects that just stopped touching
        stopped_touching = self.touched_this_frame | self.touched_last_frame

        for pair in stopped_touching:
            a = pair.objs[0]
            a = a() # unwrap weak
            if a:
                b = pair.objs[1]
                b = b() # unwrap weak
                if b:
                    if not self.leave[a][b](a, b, dt):
                        self.leave[b][a](b, a, dt)
        
        # cycle
        self.touched_last_frame = self.touched_this_frame
        self.touched_this_frame = set()

