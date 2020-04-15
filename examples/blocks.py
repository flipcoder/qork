#!/usr/bin/env qork
from random import random

block = add(2, "player.png", scale=(1, 3, 1))

block = add(Canvas(size=(0.2, 0.2)))


def update(t):
    if abs(ball.y) > 4:
        ball.vy = -ball.vy
    if abs(ball.x) > 8:
        score[ball.x > 0] += 1
        ball.pos = (0, 0, 0)
        ball.vel = randv3xy(10)

    paddle[0].vy = (key(KEY.W) - key(KEY.S)) * 10
    paddle[1].vy = (key(KEY.UP) - key(KEY.DOWN)) * 10
