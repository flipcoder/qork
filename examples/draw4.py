#!/usr/bin/env qork

canvas.clear('white')

# make a red square
red_square = canvas.batch('red')
with red_square:
    canvas.source = 'red'
    canvas.rectangle(*canvas.res/2, *canvas.res/2)
    canvas.fill()

# make a blue square
blue_square = canvas.batch('blue')
with blue_square:
    canvas.source = 'blue'
    canvas.rectangle(0, 0, *canvas.res/2)
    canvas.fill()

red_square.disconnect() # remove the red square draw calls, but leave the blue

