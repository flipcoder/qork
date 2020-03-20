#!/usr/bin/pytest
import pytest
import sys
sys.path.append('..')

from glm import vec3
from qork.util import *
from qork.node import Node
from qork.reactive import *

def increment(x):
    return x + 1

def test_signal():
    x = Wrapper(0)
    sig = Signal()
    
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

def test_lazy_capture():
    x = Lazy(lambda: 5)
    y = Lazy(lambda: x() + 1, [x])
    z = Lazy(lambda: y() + 1, [y])
    assert z.value is None
    assert z() == 7
    x.set(2)
    print(z())
    assert z() == 4
    y.set(2)
    assert z() == 3

def test_reactive():
    x = Wrapper(0)
    sig = Signal()
    sig.connect(lambda a,b,x=x: x.do(increment))
    
    y = Reactive(100, [sig])
    y(500)
    assert x() == 1
    assert y() == 500

