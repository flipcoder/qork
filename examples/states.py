#!/usr/bin/env qork

class Game(State):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('Game')
        self.canvas.text('Mode=Game. Press M.')
    def update(self, dt):
        super().update(dt)
        if key_pressed(KEY.M):
            Q.states.change(Menu)

class Menu(State):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('Menu')
        self.canvas.text('Mode=Menu. Press G.')
    def update(self, dt):
        super().update(dt)
        if key_pressed(KEY.G):
            Q.states.change(Game)

def update(dt):
    pass

Q.states.change(Game)

