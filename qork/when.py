#!/usr/bin/env python
import weakref

from .signal import Signal, Slot, Container
from .defs import *
from .util import map_range


class WhenSlot(Slot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remaining = None
        self.duration = None
        self.fade = None
        self.fade_end = None
        self.ease = None
        self.speed = 1.0
        self.range = None

    def set_speed(self, s):
        self.speed = s


class Timer(Signal):
    def __init__(self, duration, speed=1.0, when=None, lifespan=None, autoreset=True):
        super().__init__()
        self.duration = duration
        self.remaining = duration
        self.autoreset = autoreset
        self.speed = speed

        # not yet implemented
        assert lifespan is None
        assert when is None

    def __iadd__(self, t):
        if callable(t):
            self.signal.connect(f, weak=False)
        else:
            self.remaining += t
        return self

    def __isub__(self, t):
        if callable(t):
            self.signal.disconnect(f)
        else:
            self.remaining -= t
        return self

    def update(self, dt=None, autoreset=None):
        return self(dt, autoreset)

    def __call__(self, dt=None, autoreset=None):
        """
        Advance timer by dt and return True if elapsed (and reset).
        If no dt is provided, trigger the timer
        :param dt: delta time in seconds
        :param autoreset: whether to reset timer on True (elapsed)
        """
        if dt is None:
            self.remaining = 0
        else:
            self.remaining -= dt * self.speed
        if self.remaining <= 0:
            if autoreset is False or self.autoreset:
                self.remaining = max(0, self.remaining + self.duration)
            super(Signal, self).__call__(self)
            return True
        return False

    def __contains__(self, s):
        """
        Would timer elapse in s seconds?
        Example: if dt in timer: # will elapse
        """
        return s >= self.remaining

    def __bool___(self):
        return self.remaining <= 0


class When(Signal):
    """
    Fast time-based event handler
    """

    def __init__(self):
        super().__init__(T=WhenSlot)
        self.time = 0
        self.conditions = Container()

    def update_slot(self, slot, dt):
        """
        Does timer checking on a specific slot
        """

        if type(slot) == weakref.ref:
            wref = slot
            slot = slot()
            if not slot:
                if type(self.sig) == weakref.ref:
                    sig = self.sig()
                    if not sig:
                        return
                self.sig.disconnect(wref)
                return

        if slot.duration != 0:  # not infinite timer
            slot.remaining -= dt * slot.speed

        if slot.fade:
            slot.remaining = max(0.0, slot.remaining)
            p = 1.0 - (slot.remaining / slot.duration)
            slot(
                map_range(
                    # apply easing functin
                    (slot.ease(p) if slot.ease else p),
                    (0.0, 1.0),  # from range
                    slot.range_,  # to range
                )
            )
            if slot.remaining < EPSILON:
                if slot.fade_end:
                    slot.fade_end()
                slot.disconnect()  # queued
                return
        else:
            # not a fade
            if slot.remaining < EPSILON:
                if not slot.once or slot.count == 0:
                    slot()
                if slot.once:
                    slot.disconnect()  # queued
                    return
                slot.remaining = max(0.0, slot.remaining + slot.duration)  # wrap

    def update(self, dt):
        """
        Advance time by dt
        """
        self.time += dt
        for slot in self.conditions:
            if slot.value[0]():
                self.value[1]()
        for slot in self.slots:
            self.update_slot(slot, dt)
        self.refresh()

    # def __call__(self, dt):
    #     return self.update(self, dt)

    def every(self, duration, func, weak=True, once=False):
        """
        Every t seconds, call func.
        The first call is in t seconds.
        """
        slot = self.connect(func, weak)
        # if callable(t):
        #     self.duration_func = t
        #     t = t()
        # else:
        #     self.duration_func = None
        slot.duration = slot.remaining = float(duration)
        slot.once = once
        # slot.fade_end = None
        # slot.range_ = None
        return slot

    def once(self, t, func, weak=True):
        return self.every(t, func, weak, once=True)

    def fade(self, duration, range_, func, end_func=None, ease=None, weak=False):
        """
        Every frame, call function with fade value [0,1] fade value
        """
        if duration < EPSILON:
            return None
        slot = self.every(0, func, weak=weak)
        slot.duration = slot.remaining = float(duration)
        slot.fade = True
        slot.fade_end = end_func
        slot.range_ = range_
        slot.ease = ease
        return slot

    def __call__(self, t_or_cond, func, weak=True, once=False):
        if type(t) in (float, int):
            return self.every(t_or_cond, func, weak, once)
        else:

            def f(cond=t_or_cond, func=func):
                if cond():
                    func()

            return self.conditions.connect(f, once=once, weak=weak)
