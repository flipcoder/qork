#!/usr/bin/env qork
from pprint import pp

add(4, pos=lambda n: (n, 0, 0))
pp(scene.tree())
