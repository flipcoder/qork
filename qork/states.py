#!/usr/bin/env python

from .signal import Signal, Container
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
        ctor -> init() -> [ update() -> render() ] -> deinit()/del

    This class is a wrapper around reactive container, which acts as the stack.
    """
    
    def __init__(self):
        self.container = Container(reactive=True)
        
        self.pre_refresh = Signal()
        self.post_refresh = Signal()
        
        self.pending_state = None # the state currently being changed (if any)

        # explicitly set all operations on underlying container to queue
        self.container._blocked += 1
    
    def push(self, state):
        self.container.push(state)
        self.pending_state = state
        if hasattr(state, 'init'):
            self.post_refresh += state.init

    def pop(self): # schedule a pop of states
        state = self.container.top()
        if state:
            if hasattr(state, 'deinit'):
                self.pre_refresh += state.deinit
            return self.container.pop()
        else:
            return None

    def clear(self): # schedule a pop of states
        self.container.clear()

        # TODO: schedule all deinit function calls in top-down order
        # for state in reversed(self.container._slots):
            # if hasattr(state, 'deinit'):
                # self.pre_refresh += state.deinit

    def change(self, state):
        if self.container.top():
            self.container.pop()
        self.container.push(state)
    
    def update(self, dt):
        state = self.container.top()
        if hasattr(state, 'update'):
            state.update(dt)
    
    def render(self):
        state = self.container.top()
        if hasattr(state, 'render'):
            state.render()

    def refresh(self):
        self.container._blocked -= 1
        assert self.container._blocked == 0
        self.pre_refresh()
        self.container.refresh()
        self.pending_state = None
        self.post_refresh()
        self.container._blocked += 1
    
    @property
    def state(self):
        """
        NOTE: This is the current state stack top, not the pending state
        """
        return self.container.top()

