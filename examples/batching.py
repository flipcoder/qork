#!/usr/bin/env qork

Q.canvas.clear("white")

# make a red square
red_square = Q.canvas.batch("red")
with red_square:
    Q.canvas.source = "red"
    Q.canvas.canvas_rectangle(*Q.canvas.res / 2, *Q.canvas.res / 2)
    Q.canvas.fill()

# make a blue square
blue_square = Q.canvas.batch("blue")
with blue_square:
    Q.canvas.source = "blue"
    Q.canvas.canvas_rectangle(0, 0, *Q.canvas.res / 2)
    Q.canvas.fill()


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
