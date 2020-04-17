#!/usr/bin/env pytest
import sys

sys.path.append("..")

from qork.script import Script
from test_helpers import *


def test_script():
    c = Counter()

    def gen(ctx):
        c.increment()
        yield
        c.increment()

    assert c.x == 0

    script = Script(gen)

    assert c.x == 0

    script.update(1)

    assert c.x == 1

    script.update(1)

    assert c.x == 2

    assert script.done()


def test_condition():
    c = Counter()
    c2 = Counter()

    def incrementer(ctx):
        c.increment()

    def pauser(ctx):
        yield lambda: c.x == 2
        c2.increment()

    script = Script(incrementer)
    script2 = Script(pauser)

    script.update(1)
    script2.update(1)

    assert c.x == 1

    script.update(1)
    script2.update(1)

    assert c.x == 2

    assert script.done()
