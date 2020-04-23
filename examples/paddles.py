#!/usr/bin/env qork

from glm import normalize

camera.mode = '2D'

# load the ball and paddles
paddle = add(2, "player.png", scale=(0.1, 0.25, 0.1))
ball = add("player.png", scale=0.075)

# position the paddles
paddle[0].x = -.5
paddle[1].x = .5

score = [0] * 2

paddle_speed = 1


def init():
    global speed
    speed = 1
    ball.pos = (0, 0, 0)
    ball.vel = random_direction_2D(speed)


def update(t):
    if abs(ball.y) > .5:
        ball.y = ball.old_pos.y
        ball.vy = -ball.vy
    if abs(ball.x) > .5:
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

