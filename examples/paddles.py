#!/usr/bin/env qork
from random import random

# load the ball nd paddles
paddle = add(2, "player.png", scale=(1, 3, 1))
ball = add("player.png", scale=0.5)

# position the paddles
paddle[0].x = -5
paddle[1].x = 5

score = [0] * 2

# move the ball in a random direction at speed of 10
ball.vel = randv3xy(10)


def update(t):
    if abs(ball.y) > 4:
        ball.vy = -ball.vy
    if abs(ball.x) > 8:
        score[ball.x > 0] += 1
        ball.pos = (0, 0, 0)
        ball.vel = randv3xy(10)

    paddle[0].vy = (key(KEY.W) - key(KEY.S)) * 10
    paddle[1].vy = (key(KEY.UP) - key(KEY.DOWN)) * 10


@overlap(ball, paddle)
def hit(ball, paddle, dt):
    ball.x = ball.old_pos.x
    ball.vx = -ball.vx
