#!/usr/bin/env python

from .signal import Signal
import weakref


class StateMachine:
    def __init__(self, ctx, *args, **kwargs):
        self.on_state_change = Signal()
        self._states = {}
        self.ctx = weakref.ref(ctx)

    def __setitem__(self, key, val):
        # first arg is a list of states? set those instead
        # if isinstance(key, dict):
        #     self._states = key
        #     for k, v in self._states.items():
        #         self.on_state_change(k, v)
        # otherwise, the args mean what they say
        if val is None:
            del self._states[key]
        elif isinstance(key, str):
            self._states[key] = val
            self.on_state_change(key, val)
        else:
            raise Exception("state key is not a string")
        return val

    def __getitem__(self, key):
        return self._states[key]

    # def __getattr__(self, key):
    #     try:
    #         return self[key]
    #     except KeyError:
    #         raise AttributeError()

    # def __setattr__(self, key, val):
    #     self[key] = val
