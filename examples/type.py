#!/usr/bin/env qork

canvas = add(Canvas())

def script(ctx):
    msg = 'Hello there!'
    for x in range(len(msg)+1):
        canvas.clear()
        canvas.text(msg[0:x])
        yield 0.1

