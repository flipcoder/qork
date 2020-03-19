#!/usr/bin/pytest
import pytest
import sys
sys.path.append('..')

from glm import vec3
from qork.util import *
from qork.node import Node
from qork.reactive import Signal

def test_reactive():
    x = Wrapper(0)
    sig = Signal()
    def increment(x):
        return x + 1
    
    # connection and calling
    sig.connect(lambda x=x: x.do(increment))
    sig()
    assert x() == 1
    sig()
    assert x() == 2
    sig.clear()
    assert not sig.slots

    # trigger only once
    x = Wrapper(0)
    sig.once(lambda x=x: x.do(increment), 'x')
    sig()
    assert x() == 1
    assert not sig.slots # just once!
    sig()
    assert x() == 1 # nope!

