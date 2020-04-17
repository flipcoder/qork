#!/usr/bin/env pytest
import sys
import math
import pytest

sys.path.append("..")

from qork.when import When
from qork.defs import *
from test_helpers import *


def test_when():

    c = Counter()
    s = When()
    slot = s.every(2, c.increment)
    assert math.isclose(slot.t, 2)
    assert c.x == 0
    s.update(1)
    assert math.isclose(slot.t, 1)
    assert c.x == 0
    s.update(1)
    assert math.isclose(slot.t, 0)
    assert c.x == 1
    s.update(1)
    assert c.x == 1
    s.update(1)
    assert c.x == 2


def test_once():
    c = Counter()
    s = When()
    slot = s.once(2, c.increment)
    s.update(1)
    assert c.x == 0
    s.update(1)
    assert c.x == 1
    s.update(10)
    assert c.x == 1
    # s.refresh() # refresh automatically called by update()
    assert len(s) == 0
    assert slot.count == 1


def test_when_fade():

    c = Counter()
    s = When()

    s.fade(1, (0, 1), lambda t: c.increment(t), weak=False)

    s.update(0.2)

    assert c.x == pytest.approx(0.2, EPSILON)


def test_when_fade2():

    c = Counter()
    s = When()

    a = s.fade(1, (0, 1), c.increment, ease=None, weak=False)
    assert len(s) == 1

    s.update(0.1)

    assert c.x == pytest.approx(0.1, EPSILON)
    assert len(s) == 1

    s.update(0.1)

    # advanced .1 two times accumulates to .3
    # since the counter increment 2nd call is .2
    # because of interpolation
    assert c.x == pytest.approx(0.3, EPSILON)
    assert len(s) == 1


# def test_when_decorator():
#     pass
