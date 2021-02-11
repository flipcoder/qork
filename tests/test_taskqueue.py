#!/usr/bin/env pytest
import sys
import gc
import weakref

sys.path.append("..")

from qork.signal import *
from test_helpers import *

def test_taskqueue():
    w = Counter()
    tq = TaskQueue()
    assert len(tq) == 0
    assert tq._queued == [[],[]]
    assert tq._current_queue == False
    tq += w.increment
    tq += w.increment
    tq += w.increment
    assert len(tq) == 3
    tq()
    assert tq._queued == [[],[]]
    assert tq._current_queue == False
    assert len(tq) == 0
    assert w() == 3

def test_taskqueue_recursive():
    """"Queueing a task while queue is running"""
    w = Counter()
    tq = TaskQueue()
    def tq_add():
        tq.add(w.increment)
    def tq_add2():
        tq.add(tq_add)
        tq.add(tq_add)
    tq += tq_add
    tq()
    assert tq._queued == [[],[]]
    assert tq._current_queue == False
    assert w() == 1
    tq += tq_add # adds 1 to counter
    tq += tq_add2 # adds 2 to counter
    tq()
    assert w() == 4

def test_signal_taskqueue():
    """Signal queues a task while blocked"""
    w = Counter()
    tq = TaskQueue()
    sig = Signal(taskqueue=tq)
    with sig:
        sig.queue(w.increment)
        # sig.connect(w.increment, weak=False)
    assert len(tq) == 1
    assert tq() == 1
    assert len(tq) == 0
    assert w() == 1
    # assert len(sig) == 0
    assert sig.blocked == 0
    sig()
    # assert w() == 1

# def test_signal_taskqueue():
#     w = Counter()
#     tq = TaskQueue()
#     sig = Signal(taskqueue=tq)
#     def tq_add():
#         # since signal is blocked during this func add,
#         # this will be queued
#         sig.connect(w.increment, weak=False)
#     sig += tq_add
#     sig()
#     assert w() == 0
#     assert len(tq) == 1
#     tq() # task queue runs tq_add()
#     assert w() == 0
#     assert len(tq) == 0
#     sig() # signal runs w.increment
#     # assert w() == 1

