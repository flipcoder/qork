#!/usr/bin/env qork

canvas.clear("white")

# make a red square
red_square = canvas.batch("red")
with red_square:
    canvas.source = "red"
    canvas.rectangle(*canvas.res / 2, *canvas.res / 2)
    canvas.fill()

# make a blue square
blue_square = canvas.batch("blue")
with blue_square:
    canvas.source = "blue"
    canvas.rectangle(0, 0, *canvas.res / 2)
    canvas.fill()


def script(ctx):
    yield
    for x in range(3):
        red_square.disable()
        blue_square.enable()
        yield 0.5
        red_square.enable()
        blue_square.disable()
        yield 0.5
    red_square.disconnect()  # completely remove red
