#!/usr/bin/env qork
import random
from pprint import pp

# NOTE: This example isn't done yet


def flip(*lines):
    rev = list(lines)
    for i in range(len(lines)):
        rev[i] = rev[i][::-1]
    return rev


def mirror(*lines):
    return list(lines), flip(*lines)


shapes = [
    ["0000"],
    *mirror("  0", "000"),
    [" 0 ", "000"],
    *mirror("00 ", " 00"),
]
# print(shapes)

piece = None

# drop the block from the top
def drop():
    global piece
    if piece is None:
        piece = add(name="Piece", scale=0.05)
    piece.pos = (0, 0.3)
    shape = random.choice(shapes)
    for y, line in enumerate(shape):
        for x, ch in enumerate(line):
            if ch == "0":
                piece.add("player.png", name="Block", pos=(x, -y))
    # return piece


drop()

# make block fall
fall_speed = Reactive(1)


def fall():
    global piece
    piece.y -= 0.1
    # print(piece.y)
    if piece.y < -0.3:
        # piece.collapse()
        add(piece.collapse())
        drop()
        # pp(scene.tree())


falling = every(0.5, fall)
fall_speed.on_change += falling.set_speed

# @overlap('Block')
# def hit(a, b, dt):
#     global piece
#     if (a.parent == piece) != (b.parent == piece):
#         if a.parent != b.parent:
#             print('ok')
#             # piece.y += .1
#             piece.y = .8
#             piece.detach(collapse=True)
#             add(piece)
#             drop()
#             return True


def update(dt):
    global piece
    # Q.scene.pend()

    piece.x += (key_pressed(KEY.RIGHT) - key_pressed(KEY.LEFT)) * 0.1

    if key_pressed(KEY.UP):
        piece.rotate(0.25)
        for block in piece:
            block.rotate(-0.25)
    if key(KEY.DOWN):
        fall_speed(3)
    else:
        fall_speed(1)

