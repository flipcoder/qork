#!/usr/bin/env qork

Q.camera.mode = "3D"
Q.camera.z = 1.5


def script(ctx):
    while True:

        # fade black to white
        yield Q.when.fade(
            2,  # seconds
            ["black", "white"],  # range
            lambda col: Q.backdrop.gradient(col, Color(1) - col),
            ctx.resume,
        )

        # fade white to black
        yield Q.when.fade(
            2,  # seconds
            ["white", "black"],  # range
            lambda col: Q.backdrop.gradient(col, Color(1) - col),
            ctx.resume,
        )
