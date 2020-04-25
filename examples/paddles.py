#!/usr/bin/env qork

from glm import normalize

# load the ball and 2 paddles
paddle = add(2, "player.png", scale=(0.1, 0.25, 0.1))
ball = add("player.png", scale=0.075)

# prosition paddles and set speed
paddle[0].x, paddle[1].x = -0.5, 0.5
paddle_speed = 1

# set score for both players
score = [0] * 2


def init():
    global speed
    speed = 1
    ball.pos = (0, 0, 0)
    ball.vel = random_direction_2D(speed)


def update(t):
    if abs(ball.y) > 0.5:
        ball.y = ball.old_pos.y
        ball.vy = -ball.vy
    if abs(ball.x) > 0.5:
        score[ball.x > 0] += 1
        init()

    paddle[0].vy = (key(KEY.W) - key(KEY.S)) * paddle_speed
    paddle[1].vy = (key(KEY.UP) - key(KEY.DOWN)) * paddle_speed


@overlap(ball, paddle)
def hit(ball, paddle, dt):
    global speed
    ball.x = ball.old_pos.x
    speed += 0.2
    ball.vel = glm.normalize(ball.pos - paddle.pos) * speed
