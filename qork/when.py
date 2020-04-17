#!/usr/bin/env python
import weakref

from .signal import Signal
from .defs import *
from .util import map_range


class When(Signal):
    """
    Fast time-based event handler
    """

    def __init__(self):
        super().__init__()
        self.time = 0

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
            slot.remaining_t -= dt

        if slot.fade:
            slot.remaining_t = max(0.0, slot.remaining_t)
            p = 1.0 - (slot.remaining_t / slot.duration)
            slot(
                map_range(
                    # apply easing functin
                    (slot.ease(p) if slot.ease else p),
                    (0.0, 1.0),  # from range
                    slot.range_,  # to range
                )
            )
            if slot.remaining_t < EPSILON:
                if slot.fade_end:
                    slot.fade_end()
                slot.disconnect()  # queued
                return
        else:
            # not a fade
            if slot.remaining_t < EPSILON:
                if not slot.once or slot.count == 0:
                    slot()
                if slot.once:
                    slot.disconnect()  # queued
                    return
                slot.remaining_t = min(0, slot.remaining_t + slot.duration)  # wrap

    def update(self, dt):
        """
        Advance time by dt
        """
        self.time += dt
        super().each_slot(lambda slot: self.update_slot(slot, dt))
        self.refresh()

    def __call__(self, dt):
        return self.update(self, dt)

    def every(self, t, func, weak=True, once=False):
        """
        Every t seconds, call func.
        The first call is in t seconds.
        """
        slot = self.connect(func, weak)
        slot.remaining_t = slot.duration = float(t)
        slot.fade = False
        slot.ease = None
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
        slot.duration = slot.remaining_t = float(duration)
        slot.fade = True
        slot.fade_end = end_func
        slot.range_ = range_
        slot.ease = ease
        return slot
