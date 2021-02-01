#!/usr/bin/env pytest
import pytest
import sys

sys.path.append("..")
from qork.minimal import MinimalCore
from qork.controller import Controller

def test_controller():
    controller = Controller()
    app = controller.app
    assert controller.num is None
    controller.plug()
    assert controller.num == 0
    assert len(app.controllers) == 1

