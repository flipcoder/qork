#!/usr/bin/env pytest
import sys

sys.path.append("..")

from qork.util import *


# def test_util_merge():

#     @mixin
#     class Base:
#         pass

#     class Mixin:
#         def func(self):
#             return 3

#     MixBase = Base | Mixin

#     mb = MixBase()

#     assert mb.func() == 3
