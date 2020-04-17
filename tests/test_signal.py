#!/usr/bin/env pytest
import sys

sys.path.append("..")

from qork.signal import Signal
from test_helpers import *


def test_signal():

    s = Signal()
    hello = s.connect(lambda: print("hello ", end=""))
    s.connect(lambda: print("world"), weak=False)
    assert len(s) == 2
    s()  # 'hello world'

    assert s.disconnect(hello)
    s()  # 'world'
    assert len(s) == 1

    s.clear()
    assert len(s) == 0


def test_signal_queue():

    # queued connection
    c = Counter()
    s = Signal()
    s._blocked += 1
    a = s.connect(c.increment)
    assert s.queue_size() == 1
    assert c() == 1
    s()  # nothing
    s._blocked -= 1
    for func in s._queued[0]:
        print(func)
        func()
    s._queued = []
    s()  # "queued"

    # queued disconnection
    s._blocked += 1
    a.disconnect()
    assert len(s) == 1  # still attached
    assert s.queue_size() == 1
    s._blocked -= 1
    for q in s._queued:
        q()
    s._queued = []
    assert len(s) == 0


def test_signal_weak():

    s = Signal()
    w = s.connect(lambda: print("test"))
    del w
    assert len(s) == 0
    s()
    assert len(s) == 0

    s = Signal()
    w = s.connect(lambda: print("test"))
    del s  # slot outlives signal?
    assert w.sig() is None  # it works
    del w


def test_signal_once():

    s = Signal()
    w = s.once(lambda: print("test"))
    assert len(s._slots) == 1
    s()
    # assert len(s.slots) == 0
