#!/usr/bin/env python

import weakref


class Connections:
    def __init__(self, Type=list):
        self._connections = Type()

    def clear(self):
        self._connections = type(self._connections)()

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

    def __isub__(self, slot):
        for i, s in enumerate(self._connections):
            if s is slot:
                del self._connections[i]
                return self
        return self

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

    def __call__(self, *args):
        if self.dead:
            return
        func = self.func
        # if isinstance(self.func, weakref.ref):
        #     func = func()
        #     if not func:
        #         self.disconnect()
        #         return None
        r = func(*args)
        self.count += 1
        if self.once:
            self.disconnect()
        return r

    def with_item(self, action, *args):
        func = self.func
        # if isinstance(func, weakref.ref):
        #     func = func()
        #     if not func:
        #         return None
        return action(func, *args)

    def with_slot(self, action, *args):
        func = self.func
        # if isinstance(func, weakref.ref):
        #     func = func()
        #     if not func:
        #         return None
        return action(self, *args)

    def disconnect(self):
        sig = self.sig()
        if not sig:
            return None
        r = sig.disconnect(self)
        self.dead = True
        return r

    def get(self):
        func = self.func
        # if type(func) == weakref.ref:
        #     func = func()
        return func

    def __del__(self):
        self.disconnect()


class Queued:
    pass


def queued(func):
    def a(self, *args):
        if self._blocked:
            self._queued[self._queue_blocked].append(lambda: func(self, *args))
            return Queued
        self._blocked += 1
        r = func(self, *args)
        self._blocked -= 1
        self.refresh()
        return r

    return a


class Container:
    QUEUE_MAX = 256

    def __init__(self, Type=list, *args, **kwargs):

        self._slots = Type()
        self._blocked = 0
        self._queue_blocked = 0
        self._queued = [[], []]

    def __len__(self):
        return len(self._slots)

    @queued
    def __call__(self, *args):
        for slot in self._slots:
            slot(*args)

    def __iter__(self):
        return (c.get() for c in self._slots)

    def __getitem__(self, idx):
        return self._slots[idx]

    def refresh(self):
        if self._blocked == 0:
            self._blocked += 1
            self._queue_blocked += 1

            i = 0
            while True:
                if self._queued[i]:
                    for func in self._queued[i]:
                        func()
                    self.queued[i] = []
                else:
                    break
                if i >= QUEUE_MAX:
                    print("WARNING: queue maxed out")
                    assert False
                i += 1
            self.queued = [[], []]
            self._queue_blocked -= 1
            self._blocked -= 1
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

    def connect(self, func, once=False):

        if isinstance(func, (list, tuple)):
            r = []
            for f in func:
                r.append(self.connect(f, once))
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
            return slot

        # already a slot, add it
        if isinstance(func, Slot):
            slot = func  # already a slot
            slot.once = once
            self._slots.append(slot)
            return slot

        # make slot from func
        slot = Slot(func, self)
        slot.once = once
        # wslot = weakref.ref(slot) if weak else slot
        self._slots.append(slot)
        return slot

    def once(self, func):
        return self.connect(func, True)

    @queued
    def disconnect(self, slot):

        if isinstance(slot, Slot):
            for i in range(len(self._slots)):
                islot = self._slots[i]
                if islot is slot:
                    del self._slots[i]
                    return True

        else:
            # delete by slot value
            value = slot
            for i in range(len(self._slots)):
                slot = self._slots[i]
                func = slot.func
                if func is value:
                    del self._slots[i]
                    return True

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
        self.clear()

    def __enter__(self):
        assert not self._blocked
        self._blocked += 1

    def __exit__(self, typ, val, tb):
        self._blocked -= 1
        assert not self._blocked
        if self._blocked == 0:
            self.refresh()

    def __contains__(self, element):
        return element in iter(x.get() for x in self._slots)


def passthrough(s):
    return s


class Signal(Container):
    def __init__(self, *args, **kwargs):

        super().__init__(Type=list, *args, **kwargs)
        if args:
            self.adapter = args.pop(0) if args else noop
        else:
            self.adapter = passthrough

    def __call__(self, *args):

        self._blocked += 1
        for slot in self._slots:
            if isinstance(slot, weakref.ref):
                wref = slot
                slot = wref()
                if slot is None:
                    self.disconnect(wref)  # we're blocked, so this will queue
            if slot is not None and not slot.dead:
                slot(*args)
        self._blocked -= 1

        self.refresh()

    def queue(self, func):
        self._queued.append(func)

    def refresh(self):
        if self._blocked == 0:
            for wref in self._slots:
                if isinstance(wref, weakref.ref):
                    slot = wref()
                    if not slot:
                        self.disconnect(wref)
                    elif isinstance(slot.func, weakref.ref):
                        wfunc = slot.func()
                        if not wfunc:
                            self.disconnect(wref)

            super().refresh()

    def each(self, func, *args):
        if self._blocked:
            self._queued.append(lambda func=func, args=args: self.each(func, *args))
            return None

        self._blocked += 1
        for s in self._slots:
            if isinstance(s, weakref.ref):
                wref = s
                s = wref()
                if not func:
                    self.disconnect(wref)
                    continue
            s.with_item(func, *args)
        self._blocked -= 1

        self.refresh()

    def each_slot(self, func, *args):
        if self._blocked:
            self._queued.append(
                lambda func=func, args=args: self.each_slot(func, *args)
            )
            return None

        self._blocked += 1
        for s in self._slots:
            if isinstance(s, weakref.ref):
                s = s()
                if not s:
                    continue
            s.with_slot(func, *args)
        self._blocked -= 1

        self.refresh()

    def __iadd__(self, func):
        self.connect(func, weak=False)
        return self

    def __isub__(self, func):
        self.disconnect(func)
        return self

    def connect(self, func, weak=True, once=False):

        if isinstance(func, (list, tuple)):
            r = []
            for f in func:
                r.append(self.connect(f, weak, once))
            return r

        if self._blocked:
            # if we're blocked, then queue the call
            if isinstance(func, Slot):
                slot = func
            else:
                slot = Slot(self.adapter(func), self)
            slot.once = once
            wslot = weakref.ref(slot) if weak else slot
            self._queued.append(lambda wslot=wslot: self._slots.append(wslot))
            return slot

        # already a slot, add it
        if isinstance(func, Slot):
            slot = func  # already a slot
            slot.once = once
            self._slots.append(slot)
            return slot

        # make slot from func
        slot = Slot(self.adapter(func), self)
        slot.once = once
        wslot = weakref.ref(slot) if weak else slot
        self._slots.append(wslot)
        return slot

    def once(self, func, weak=True):
        return self.connect(func, weak, True)

    def disconnect(self, slot):
        if self._blocked:
            self._queued.append(lambda slot=slot: self.disconnect(slot))
            return None

        if isinstance(slot, weakref.ref):
            # try to remove weak reference
            wref = slot
            slot = wref()
            for i in range(len(self._slots)):
                if slot:  # weakref dereffed?
                    if self._slots[i] is slot:
                        del self._slots[i]
                        return True
                if self._slots[i] is wref:
                    del self._slots[i]
                    return True
        elif isinstance(slot, Slot):
            for i in range(len(self._slots)):
                islot = self._slots[i]
                if isinstance(islot, weakref.ref):
                    islot = islot()
                    if not islot:
                        return True
                    if islot is slot:
                        del self._slots[i]
                        return True
                else:
                    if islot is slot:
                        del self._slots[i]
                        return True

        else:
            # delete by slot value
            value = slot
            for i in range(len(self._slots)):
                slot = self._slots[i]
                if isinstance(slot, weakref.ref):
                    wref = slot
                    slot = slot()
                    if not slot:
                        return self.disconnect(wref)
                func = slot.func
                # func = slot.func
                # if isinstance(func, weakref.ref):
                #     wref = func
                #     func_unpacked = func()
                #     if not func:
                #         return self.disconnect(wref)
                if func is value:
                    del self._slots[i]
                    return True

        return False

    def clear_type(self, Type):
        if self._blocked:
            self._queued.append(lambda: self.clear_type())
            return None

        self._blocked += 1
        for slot in self._slots:
            if isinstance(slot.get(), Type):
                slot.disconnect()
        self._blocked -= 1
        self.refresh()

    def filter(self, func):
        if self._blocked:
            self._queued.append(lambda f, slot=slot: self.filter(func))
            return None

        self._blocked += 1
        for slot in self._slots:
            if func(slot.get()):
                slot.disconnect()
        self._blocked -= 1
        self.refresh()

    def find(self, func, default=None):
        for ch in self._slots:
            if func(ch):
                return ch
        return default
