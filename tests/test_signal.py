#!/usr/bin/env pytest
import sys
import gc
import weakref

sys.path.append("..")

from qork.signal import *
from test_helpers import *

def test_container():
    c = Container()
    assert len(c) == 0
    s = lambda: 0
    c += s
    assert len(c) == 1
    c -= s
    assert len(c) == 0

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

    c = Counter()
    s = Signal()
    a = None

    # queued connection
    with s:
        a = s.connect(c.increment)
        assert len(s) == 0
        assert s.queue_size() == 1
        s()
        assert c() == 0
    assert len(s) == 1
    assert s.queue_size() == 0
    assert c() == 0

    # queued disconnection
    with s:
        assert a.disconnect() is None
        assert len(s) == 1  # still there
        assert s.queue_size() == 1  # disc queued?

    assert len(s) == 0
    assert s.queue_size() == 0

    # for q in s._queued[0]:
    #     q()
    # s._queued = []
    assert len(s) == 0


def test_signal_slot_del():

    s = Signal()
    w = s.connect(lambda: print("test"))
    del w
    assert len(s) == 0


def test_signal_dies_first():

    s = Signal()
    w = s.connect(lambda: print("test"))
    del s  # slot outlives signal
    assert w.sig() is None  # it works


def test_signal_weak_deletions():
    s = Signal()
    c = s.connect(lambda: print("test1"))
    assert len(s) == 1
    s.disconnect(c)  # w delete from sig?
    assert len(s) == 0
    del c

    s = Signal()
    c = s.connect(lambda: print("test2"))
    assert len(s) == 1
    c.disconnect()  # delete from w?
    assert len(s) == 0
    del c

    s = Signal()
    c = s.connect(lambda: print("test3"))
    assert len(s) == 1
    s2 = Signal()
    other_slot = s2.connect(lambda: None)
    assert s.disconnect(other_slot) is False  # wrong signal!
    assert len(s) == 1
    # s.disconnect(weakref.ref(c)) # delete from wref
    # assert len(s) == 0


def test_signal_once():

    s = Signal()
    w = s.once(lambda: print("test"))
    assert len(s._slots) == 1
    s()
    # assert len(s.slots) == 0

def test_signal_tags():

    s = Signal()
    assert len(s) == 0
    s.connect((lambda: 1), weak=False, tags=['foo'])
    assert len(s) == 1
    assert(s._slots[0].tags == {'foo'})
    s.clear_tag('foo')
    assert len(s) == 0

