#!/usr/bin/env qork

camera.mode = "3D"
camera.z = 1.5

def script(ctx):
    while True:

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

