#!/usr/bin/env pytest

import sys
sys.path.append("..")
from qork.states import StateMachine, StateStack

class DebugState():
    def __init__(self):
        self.init_calls = 0
        self.deinit_calls = 0
        self.update_calls = 0
        self.render_calls = 0
    def init(self):
        self.init_calls += 1
        print('state init')
    def update(self, dt):
        self.update_calls += 1
        print('update init')
    def render(self):
        self.render_calls += 1
        print('render init')
    def deinit(self):
        self.deinit_calls += 1
        print('state deinit')

def test_statestack():
    ss = StateStack()
    debug_state = DebugState()
    ss.push(debug_state)
    assert debug_state.init_calls == 0
    assert ss.pending_state == debug_state
    
    ss.refresh() # do state changes now
    assert debug_state.init_calls == 1
    
    assert ss.pending_state == None
    assert ss.state == debug_state

    assert debug_state.update_calls == 0
    ss.update(1.0)
    assert debug_state.update_calls == 1
    
    assert debug_state.render_calls == 0
    ss.render()
    assert debug_state.render_calls == 1

    assert debug_state.deinit_calls == 0
    ss.pop();
    assert debug_state.deinit_calls == 0 # still 0 (queued)
    ss.refresh()
    assert debug_state.deinit_calls == 1

