#!/usr/bin/env qork
from pprint import pp

Q.add(4, pos=lambda n: (n, 0, 0))
pp(Q.scene.tree())
