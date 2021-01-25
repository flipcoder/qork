#!/usr/bin/env pytest
import pytest
import sys

sys.path.append("..")

from glm import vec3
from qork.util import *
from qork.node import Node
from qork.reactive import *

from test_helpers import *

# def test_signal():
#     x = Wrapper(0)
#     sig = Signal()

#     # connection and calling
#     sig.connect(lambda x=x: x.do(increment))
#     sig()
#     assert x() == 1
#     sig()
#     assert x() == 2
#     sig.clear()
#     assert not sig.slots

#     # trigger only once
#     x = Wrapper(0)
#     sig.once(lambda x=x: x.do(increment))
#     sig()
#     assert x() == 1
#     assert not sig.slots # just once!
#     sig()
#     assert x() == 1 # nope!


def test_lazy_capture():
    x = Lazy(lambda: 5)
    y = Lazy(lambda: x() + 1, [x])
    assert len(x.on_pend) == 1
    z = Lazy(lambda: y() + 1, [y])
    assert len(y.on_pend) == 1
    assert z.value is None
    assert z() == 7
    x(2)
    assert z() == 4
    y(2)
    assert z() == 3

def test_weaklambda():
    x = Wrapper(5)
    getx = WeakLambda([x], lambda x: x() + 5)
    assert getx() == 10
    assert not getx.dead()
    del x
    assert getx.dead()

def test_reactive():
    x = Counter()
    sig = Signal()
    sig += x.increment

    y = Reactive(100, [sig])
    y(500)
    assert x() == 1
    assert y() == 500
