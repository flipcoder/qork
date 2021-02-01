#!/usr/bin/env pytest
import pytest
import sys

sys.path.append("..")
from qork.minimal import MinimalCore
from qork.session import Session

def test_session():
    session = Session()
    app = session.app


