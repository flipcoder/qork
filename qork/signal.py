#!/usr/bin/env python

import weakref


class Connections:
    def __init__(self, Storage=list):
        self.Storage = Storage
        self._connections = Storage()

    def remove(self, con):
        self -= con

    def clear(self):
        self._connections = self.Storage()

    def __bool__(self):
        return bool(self._connections)

    def __len__(self):
        return len(self._connections)

    def __contains__(self, item):
        return item in iter(self._connections)

    def __iadd__(self, slot):
        assert slot is not None
        if isinstance(slot, (tuple, list)):
            self._connections += slot
            return self
        self._connections.append(slot)
        return self

    def __isub__(self, con):
        for i, c in enumerate(self._connections):
            if c is con:
                del self._connections[i]
                return self
        return self

    def __delitem__(self, con):
        self -= con

    # backwards compat with list
    def append(self, slot):
        assert slot is not None
        self._connections.append(slot)
        return self

    def __iter__(self):
        return iter(self._connections)

    def __getitem__(self, idx):
        return self._connections[idx]


class Slot:
    def __init__(self, func, sig):
        self.func = func
        self.sig = weakref.ref(sig)
        self.once = False
        self.count = 0
        self.dead = False
        self.on_remove = Signal()

    def __call__(self, *args, **kwargs):
        if self.dead:
            return
        func = self.func
        # if isinstance(self.func, weakref.ref):
        #     func = func()
        #     if not func:
        #         self.disconnect()
        #         return None
        r = func(*args, **kwargs)
        self.count += 1
        if self.once:
            self.disconnect()
            self.on_remove(self)
        return r

    def with_item(self, action, *args, **kwargs):
        return action(self.func, *args)

    def with_slot(self, action, *args, **kwargs):
        return action(self, *args)

    def disconnect(self):
        if self.dead:
            return None
        sig = self.sig()
        if not sig:
            return None
        self.dead = True
        self.on_remove(self)
        return sig.disconnect(self)

    def get(self):
        return self.func

    def __del__(self):
        if self.dead:
            return
        self.disconnect()
        self.on_remove(self)
        self.dead = True


class Queued:
    pass


def passthrough(*args):
    return args[0] if args else None


def queued(func):
    def queued_decorator(self, *args, **kwargs):
        if self._blocked:
            self.queue(lambda a=args, kw=kwargs: func(self, *a, **kw))
            return None
        self._blocked += 1
        r = func(self, *args, **kwargs)
        if type(r) is tuple:
            cb = r[1]
            arg = r[2]
            r = r[0]
        else:
            cb = None
        self._blocked -= 1
        self.refresh()
        if cb is not None:
            cb(arg)
        return r

    return queued_decorator


class Container:
    def __init__(
        self, adapter=None, Storage=list, Element=None, reactive=False, *args, **kwargs
    ):
        """
        A safely-iterable container where all operations during iterations
        are queued and processed after.
        Similar to signal, but does not support slot weakrefs.
        """

        self.Storage = Storage
        self.Element = Element
        self._slots = Storage()
        self._blocked = 0
        self._current_queue = 0
        self._queued = [[], []]  # two ping-pong queues
        self.adapter = adapter

        if reactive:
            self.on_change = self.on_pend = Signal()

    def queue_size(self):
        return len(self._queued[0]) + len(self._queued[1])

    def queue(self, func):
        if self._blocked:
            self._queued[self._current_queue].append(func)
            return True
        func()
        return False

    # decorator
    def do(self):
        """
        @mycontainer.do
        def do_this_now_or_queue_if_blocked():
            pass
        """

        def do_decorator(func):
            if self._blocked:
                self._queued[self._current_queue].append(lambda: func(self, *args))
                return
            self._blocked += 1
            func()
            self._blocked -= 1
            self.refresh()

        return do_decorator

    @property
    def slots(self):
        if self.Storage == list:
            itr = iter(self._slots)
        else:
            return iter(self._slots.values())

        itr = iter(self._slots)
        with self:
            for slot in itr:
                yield slot

    @property
    def items(self):
        if self.Storage == list:
            itr = enumerate(self._slots)
        else:
            return iter(self._slots.values())

        itr = iter(self._slots)
        with self:
            for i, slot in itr:
                yield i, slot.get()

    def __len__(self):
        return len(self._slots)

    @queued
    def __call__(self, *args, **kwargs):
        for slot in self._slots:
            slot(*args, **kwargs)

    def __iter__(self):
        return (c.get() for c in self.slots)

    def __getitem__(self, idx):
        return self._slots[idx].func

    def __delitem__(self, slot):
        self -= slot

    def refresh(self):
        if self._blocked == 0:
            # self._blocked += 1
            self._current_queue += 1

            i = False
            while True:
                if self._queued[i]:
                    for func in self._queued[i]:
                        func()
                    self._queued[i] = []
                else:
                    break
                i = not i  # ping pong

            assert self._queued == [[], []]
            self._current_queue -= 1

            # self._blocked -= 1
            return True
        return False

    @queued
    def each(self, func, *args):
        for s in self._slots:
            s.with_item(func, *args)

    @queued
    def each_slot(self, func, *args):
        for s in self._slots:
            s.with_slot(func, *args)

    def __iadd__(self, func):
        self.connect(func)
        return self

    def __isub__(self, func):
        self.disconnect(func)
        return self

    def __bool__(self):
        return bool(self._slots)

    def connect(self, func, once=False, cb=None):

        if isinstance(func, (list, tuple)):
            r = []
            for f in func:
                r.append(self.connect(f, once, cb))
            return r

        if self._blocked:
            # if we're blocked, then queue the call
            if isinstance(func, Slot):
                slot = func
            else:
                slot = Slot(func, self)
            slot.once = once
            # wslot = weakref.ref(slot) if weak else slot
            # self._queued.append(lambda wslot=wslot: self._slots.append(wslot))
            if cb:
                cb(slot)
            return slot

        # already a slot, add it
        if isinstance(func, Slot):
            slot = func  # already a slot
            slot.once = once
            self._slots.append(slot)
            if cb:
                cb(slot)
            return slot

        # make slot from func
        slot = Slot(func, self)
        slot.once = once
        # wslot = weakref.ref(slot) if weak else slot
        self._slots.append(slot)
        if cb:
            cb(slot)
        return slot

    def once(self, func, cb=None):
        return self.connect(func, weak=True, cb=cb)

    @queued
    def disconnect(self, slot, cb=None):

        # delete by key
        if self.Element == dict and type(slot) == str:
            del self._slots[slot]
            return None, cb, slot

        if isinstance(slot, Slot):
            for i in range(len(self._slots)):
                islot = self._slots[i]
                if islot is slot:
                    del self._slots[i]
                    return True, cb, i

        else:
            # delete by slot value
            value = slot
            for i in range(len(self._slots)):
                slot = self._slots[i]
                func = slot.func
                if func is value:
                    del self._slots[i]
                    return True, cb, i

        return False

    @queued
    def clear_type(self, Type):
        for slot in self._slots:
            if isinstance(slot.get(), Type):
                slot.disconnect()

    @queued
    def filter(self, func):
        for slot in self._slots:
            if func(slot.get()):
                slot.disconnect()

    @queued
    def clear(self):
        b = bool(len(self._slots))
        self._slots = []
        return b

    @queued
    def sort(self, key=None):
        if key is None:
            self._slots.sort()
            return self

        self._slots = sorted(self._slots, key=lambda x: key(x))
        return self

    def __del__(self):
        assert not self._blocked
        self.clear()

    def __enter__(self):
        self._blocked += 1

    def __exit__(self, typ, val, tb):
        self._blocked -= 1
        if self._blocked == 0:
            self.refresh()

    def __contains__(self, element):
        return element in iter(x.get() for x in self._slots)

    def __iter__(self):
        with self:
            for slot in self._slots:
                yield slot.get()

    # stack functions

    @queued
    def push(self, e):
        self._slots.append(e)
        self.on_pend()
        return e

    @queued
    def pop(self):
        e = self.slots[-1]
        self._slots = self._slots[:-1]
        self.on_pend()
        return e

    def top(self):
        return self._slots[-1]


class Signal(Container):
    def __init__(self, simple=False, T=Slot, *args, **kwargs):
        super().__init__(*args, Element=T, **kwargs)
        self.on_connect = passthrough if simple else Signal(simple=True)

    def __call__(self, *args, **kwargs):
        with self:
            for slot in self._slots:
                if isinstance(slot, weakref.ref):
                    wref = slot
                    slot = wref()
                    if not slot:
                        self.disconnect(wref)  # we're blocked, so this will queue
                        continue
                if slot is not None and not slot.dead:
                    slot(*args)

    def refresh(self):
        if self._blocked == 0:
            for wref in self._slots:
                if isinstance(wref, weakref.ref):
                    slot = wref()
                    if not slot:
                        self.disconnect(wref)

            super().refresh()

    @queued
    def each(self, func, *args):
        for s in self._slots:
            if isinstance(s, weakref.ref):
                wref = s
                s = wref()
                if not func:
                    self.disconnect(wref)
                    continue
            s.with_item(func, *args)

    @queued
    def each_slot(self, func, *args):
        for s in self._slots:
            if isinstance(s, weakref.ref):
                s = s()
                if not s:
                    continue
            s.with_slot(func, *args)

    def __iadd__(self, func):
        self.connect(func, weak=False)
        return self

    def __isub__(self, func):
        self.disconnect(func)
        return self

    def _adapt(self, func):
        """
        Returns the function with applied adapter
        """
        return self.adapter(func) if self.adapter else func

    def iterslots(self):
        with self:
            for slot in self._slots:
                if type(slot) == weakref.ref:
                    wref = slot
                    slot = wref()
                yield slot

    def __iter__(self):
        return (x.get() for x in self.iterslots())

    def connect(self, func, weak=True, once=False, cb=None, on_remove=None):

        if isinstance(func, (list, tuple)):
            r = []
            for f in func:
                r.append(self.connect(f, weak, once, cb, on_remove))
            return r

        if self._blocked:
            # if we're blocked, then queue the call
            if isinstance(func, self.Element):
                slot = func
            else:
                slot = self.Element(self, self._adapt(func))
            slot.once = once
            # wslot = weakref.ref(slot) if weak else slot
            self._queued[self._current_queue].append(
                lambda slot=slot: self.connect(slot, weak, cb=cb)
            )
            if on_remove:
                slot.on_remove.connect(on_remove, weak=False)
            return slot

        # already a slot, add it
        if isinstance(func, self.Element):
            slot = func  # already a slot
            slot.sig = weakref.ref(self)
            slot.once = once
            self._slots.append(slot)
            self.on_connect(slot)
            if on_remove:
                slot.on_remove.connect(on_remove, weak=False)
            if cb:
                cb()
            return slot

        # make slot from func
        slot = self.Element(self._adapt(func), self)
        slot.once = once
        wslot = weakref.ref(slot) if weak else slot
        self._slots.append(wslot)
        self.on_connect(slot)
        if on_remove:
            slot.on_remove.connect(on_remove, weak=False)
        if cb:
            cb()
        return slot

    def once(self, func, weak=True):
        return self.connect(func, weak, once=True)

    def disconnect(self, slot, cb=None):

        if self._blocked:
            self.queue(lambda slot=slot: self.disconnect(slot, cb))
            return None

        if not self._slots:
            return False

        if isinstance(slot, weakref.ref):
            # try to remove weak reference
            wref = slot
            slot = wref()
            for i in range(len(self._slots)):
                # if slot:  # weakref?
                if self._slots[i] is slot:
                    del self._slots[i]
                    if cb:
                        cb()
                    return True
                # if self._slots[i] is wref:
                #     print('del')
                #     del self._slots[i]
                #     return True
            return False
        elif isinstance(slot, self.Element):
            # try to remove slot
            r = False
            clean_wrefs = False
            for i in range(len(self._slots)):
                islot = self._slots[i]
                if isinstance(islot, weakref.ref):
                    islot = islot()
                    if not islot:
                        clean_wrefs = True
                    if islot is slot:
                        del self._slots[i]
                        r = True
                        break
                else:
                    if islot is slot:
                        del self._slots[i]
                        r = True
                        break
            if clean_wrefs:
                self._slots = list(filter(lambda s: s(), self._slots))
            if cb:
                cb(i)
            return r

        else:
            # delete by slot value
            value = slot
            clean_wrefs = False
            for i in range(len(self._slots)):
                slot = self._slots[i]
                if isinstance(slot, weakref.ref):
                    wref = slot
                    slot = slot()
                    if not slot:
                        # clean_wrefs = True
                        # self._slots = list(filter(lambda s: s(), self._slots))
                        r = self.disconnect(wref)
                        if cb:
                            cb(wref)
                        return r
                # func = slot.func
                # func = slot.func
                # if isinstance(func, weakref.ref):
                #     wref = func
                #     func_unpacked = func()
                #     if not func:
                #         return self.disconnect(wref)
                if func is value:
                    del self._slots[i]
                    if cb:
                        cb(i)
                    return True
            return False

    def clear_type(self, Type):
        if self._blocked:
            self.queue(self.clear_type)
            return None

        with self:
            for slot in self._slots:
                if isinstance(slot.get(), Type):
                    slot.disconnect()

    def filter(self, func):
        if self._blocked:
            self.queue(lambda f=func: self.filter(func))
            return None  # return promise?

        with self:
            for slot in self._slots:
                if func(slot.get()):
                    slot.disconnect()

    def find(self, func):
        for ch in self._slots:
            if func(ch):
                return ch
        return None
