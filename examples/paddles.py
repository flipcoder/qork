#!/usr/bin/env qork

from glm import normalize
from glm import vec2

# load the ball and 2 paddles
# paddle = add(2, "player.png", scale=(0.1, 0.25, 0.1))
paddle = [None] * 2
paddle[0] = add(Canvas(color="white", res=ivec2(1), scale=(0.1, 0.25, 0.1)))
paddle[1] = add(Canvas(color="white", res=ivec2(1), scale=(0.1, 0.25, 0.1)))

ball = add(Canvas(color="white", res=ivec2(1), scale=0.05))
# ball = add("player.png", scale=0.05)

# prosition paddles and set speed
edge = 0.75
paddle[0].x, paddle[1].x = -edge, edge
paddle_speed = 1

# set score for both players
score = [0] * 2

# hud.y = .4


def refresh_score():
    canvas.clear()
    canvas.text(" - ".join(map(lambda s: str(s), score)), "white", vec2(0, 128), "h")


refresh_score()


def init():
    global speed
    speed = 1
    ball.pos = (0, 0, 0)
    ball.vel = random_direction_2D(speed)


def update(t):
    if abs(ball.y) > 0.5:
        ball.y = ball.old_pos.y
        ball.vy = -ball.vy
    if abs(ball.x) > edge + 0.2:
        score[ball.x > 0] += 1
        refresh_score()
        # hud.clear()
        # hud.text(str(score[0]) + ' - ' + str(score[1]), hud.res/2, 'white', 'hv')
        init()

    paddle[0].vy = (key(KEY.W) - key(KEY.S)) * paddle_speed
    paddle[1].vy = (key(KEY.UP) - key(KEY.DOWN)) * paddle_speed


@overlap(ball, paddle)
def hit(ball, paddle, dt):
    global speed
    ball.x = ball.old_pos.x
    speed += 0.2
    ball.vel = normalize(ball.pos - paddle.pos) * speed
