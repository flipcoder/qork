#!/usr/bin/env pytest

import sys

sys.path.append("..")
from qork.state import State
from qork.states import StateMachine, StateStack


class DebugState(State):
    def __init__(self):
        self.init_calls = 0
        self.deinit_calls = 0
        self.update_calls = 0
        self.render_calls = 0

    def init(self):
        self.init_calls += 1

    def update(self, dt):
        self.update_calls += 1

    def render(self):
        self.render_calls += 1

    def deinit(self):
        self.deinit_calls += 1


def test_statestack_factory():
    ss = StateStack()
    ss.push(DebugState)  # ctor as factory func

    assert len(ss.pending_states) == 1
    # assert debug_state.init_calls == 0

    assert type(ss.pending_states[-1]) is StateStack.FactoryFunctionWrapper
    assert type(ss.pending_states[-1].func) is type
    assert ss.pending_states[-1].func is DebugState

    ss.refresh()  # do state changes now

    assert len(ss.container._slots) == 1
    debug_state = ss.state
    assert debug_state.init_calls == 1

    debug_state = ss.state

    assert ss.pending_states == []
    assert type(ss.state) is DebugState

    assert debug_state.update_calls == 0
    ss.update(1.0)
    assert debug_state.update_calls == 1

    assert debug_state.render_calls == 0
    ss.render()
    assert debug_state.render_calls == 1

    assert debug_state.deinit_calls == 0
    ss.pop()
    assert debug_state.deinit_calls == 0  # still 0 (queued)
    ss.refresh()
    assert debug_state.deinit_calls == 1


def test_statestack_direct():
    ss = StateStack()
    debug_state = DebugState()
    # ss._push_state_direct(debug_state)
    ss.push(debug_state)  # STATE, not factory function
    assert len(ss.pending_states) == 0
    assert debug_state.init_calls == 0

    # assert type(ss.pending_states[-1]) is StateStack.FactoryFunctionWrapper
    # assert type(ss.pending_states[-1].func) is type
    # assert ss.pending_states[-1].func is DebugState

    ss.refresh()  # do state changes now
    assert debug_state.init_calls == 1

    assert ss.pending_states == []
    assert type(ss.state) is DebugState

    assert debug_state.update_calls == 0
    ss.update(1.0)
    assert debug_state.update_calls == 1

    assert debug_state.render_calls == 0
    ss.render()
    assert debug_state.render_calls == 1

    assert debug_state.deinit_calls == 0
    ss.pop()
    assert debug_state.deinit_calls == 0  # still 0 (queued)
    ss.refresh()
    assert debug_state.deinit_calls == 1
