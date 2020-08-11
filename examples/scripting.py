#!/usr/bin/env qork


def script(ctx):
    while True:
        print("tick")
        yield ctx.sleep(1)
