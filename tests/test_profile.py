#!/usr/bin/env pytest
import pytest
import sys

sys.path.append("..")
from qork.minimal import MinimalCore
from qork.profile import Profile

def test_profile():
    profile = Profile()
    app = profile.app
    assert profile.num is None
    profile.enable()
    assert profile.num == 0
    assert len(app.profiles) == 1

