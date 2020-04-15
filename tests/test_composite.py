#!/usr/bin/env pytest
import sys

sys.path.append("..")

from qork.composite import *

from test_helpers import *


class DogA:
    def woof(self):
        return "a"


class DogB:
    def woof(self):
        return "b"


# def test_mixin():
#     DogAB = Mixin(Wrapper, DogA)

#     dog = DogAB()

#     assert dog.woof() == "a"


def test_composite():

    c = Composite(DogA(), DogB())

    assert c.woof() == ["a", "b"]
