#!/usr/bin/env qork

class GameState(State):
    def __init__(self):
        print("game started")
    def update(self, dt):
        print("update(dt)")
    def render(self):
        print("render()")
    def deinit(self):
        print("deinit")

Q.states.push(GameState)

