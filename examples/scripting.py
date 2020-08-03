#!/usr/bin/env qork

console(False)


def script(ctx):
    while True:
        print("tick")
        yield ctx.sleep(1)
