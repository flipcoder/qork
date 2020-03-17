#!/usr/bin/env python

import itertools

# buttons
LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3

# space
LOCAL = 0
PARENT = 1
WORLD = 2

EPSILON = 0.00001

def flatten(r):
    return tuple(itertools.chain(*r))

