#!/usr/bin/env qork
add("test.ogg").play()


@delay(0.1)
def later():
    add("test.wav").play()
