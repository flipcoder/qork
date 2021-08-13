#!/usr/bin/env qork
Q.add("test.ogg").play()


@delay(0.1)
def later():
    Q.add("test.wav").play()
