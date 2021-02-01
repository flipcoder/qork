#!/usr/bin/env python

from .signal import Signal, Container
from .minimal import StateBase
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


class StateStack:
    """
    State stack maintains core game state transitions and update/render calls

    A state can have (all optional):
        factory func -> ctor -> [ update() -> render() ] -> deinit()/del

    This class is a wrapper around reactive container, which acts as the stack.
    """

    """
    A wrapper to discern between a State duck type and a function
        (since states can have call operators too)
    """

    class FactoryFunctionWrapper:
        # func = ...
        def __init__(self, func=None):
            self.func = func

        def __call__(self):
            return self.func()

    def __init__(self):
        self.container = Container(reactive=True)

        self.pre_refresh = Signal()
        self.post_refresh = Signal()
        self.on_pending_state = Signal()

        self.pending_states = []  # the states currently being changed (if any)

        # explicitly set all operations on underlying container to queue
        self.container._blocked += 1

    def _push_state_direct(self, state):
        self.container.push(state)
        if hasattr(state, "init"):
            self.post_refresh.once(state.init, weak=False)

    def push(self, state):
        """
        Push a state, a state class, or a "factory" function that creates a state.
        If a state is pushed directly the ctor will have been already called by you.
        If you want the state ctor deferred until AFTER the other states clean up
        (deinit()), then pass the state class or creation function instead.
        """

        if isinstance(state, StateBase):
            # print("1")
            # Pushing state directly
            self._push_state_direct(state)
        else:
            # print("2")
            # Factory function, create during refresh
            self.pending_states.append(StateStack.FactoryFunctionWrapper(state))
            # self.container.push(state)

    def pop(self):  # schedule a pop of states
        state = self.container.top()
        if state:
            if hasattr(state, "deinit"):
                self.pre_refresh += state.deinit
            return self.container.pop()
        else:
            return None

    def clear(self, state=None):  # schedule a pop of states
        """
        Clear state stack and optionally push a state or state factory function `state`
        """
        self.container.clear()

        # schedule all deinit function calls in top-down order
        for state in reversed(self.container._slots):
            if hasattr(state, "deinit"):
                self.pre_refresh.once(state.deinit, weak=False)

        if state is not None:
            self.container.push(state)

    def change(self, state):
        # self.pending_pop = True
        # def poptop():
        if self.container.top():
            self.container.pop()
        # self.pending_opertaions.append(poptop)
        self.push(state)

    def update(self, dt):
        state = self.container.top()
        if hasattr(state, "update"):
            state.update(dt)

    def render(self):
        state = self.container.top()
        if hasattr(state, "render"):
            state.render()

    def refresh(self):
        assert self.container._blocked == 1

        # if self.pending_operations:
        #     while self.pending_operations:
        #         ops = self.pending_operations[:]
        #         self.pending_operations = []
        #         for op in ops:
        #             op()

        # for each state factory fuction, call it here to create the state
        if self.pending_states:
            for i in range(len(self.pending_states)):
                state_func = self.pending_states[i]
                if type(state_func) is StateStack.FactoryFunctionWrapper:
                    # unwrap factory function and call it, replacing state
                    self._push_state_direct(state_func())
                    self.on_pending_state(state_func)
            self.pending_states = []

        self.container._blocked -= 1
        assert self.container._blocked == 0

        # pre-refresh signal
        self.pre_refresh()

        # now that underlying container is unblocked, run queued operations
        self.container.refresh()

        # post-refresh signal
        self.post_refresh()

        # block underlying container again
        self.container._blocked += 1

    @property
    def state(self):
        """
        NOTE: This is the current state stack top, not the pending state
        """
        return self.container.top()
