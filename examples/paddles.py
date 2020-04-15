#!/usr/bin/env qork

camera.ortho = True

# load the ball and paddles
paddle = add(2, "player.png", scale=(0.2, 0.5, 0.2))
ball = add("player.png", scale=0.15)

# position the paddles
paddle[0].x = -1
paddle[1].x = 1

score = [0] * 2

speed = 2
paddle_speed = 2

from glm import normalize


def init():
    global speed
    speed = 2
    ball.pos = (0, 0, 0)
    ball.vel = random_direction_2D(speed)


def update(t):
    normalize
    if abs(ball.y) > 1:
        ball.y = ball.old_pos.y
        ball.vy = -ball.vy
    if abs(ball.x) > 1:
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
