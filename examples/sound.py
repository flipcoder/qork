#!/usr/bin/env qork
add("test.ogg")


@delay(0.1)
def later():
    add("test.wav")
