#!/usr/bin/env qork

camera.mode = "3D"
camera.z = 1.5

def init():
    canvas.source = 'red'
    canvas.rectangle(.25, .25, .5, .5)
    canvas.fill()

def script(ctx):
    while True:
        init()

        # fade black to white
        yield when.fade(
            2, # seconds
            ["black", "white"], # range
            lambda col: backdrop.gradient(col, Color(1) - col),
            ctx.resume
        )

        # fade white to black
        yield when.fade(
            2, # seconds
            ["white", "black"], # range
            lambda col: backdrop.gradient(col, Color(1) - col),
            ctx.resume
        )

