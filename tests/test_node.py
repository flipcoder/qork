#!/usr/bin/pytest
import pytest
import sys
sys.path.append('..')

from glm import vec3
from qork.util import *
from qork.node import Node

class MockApp:
    def __init__(self):
        self.ctx = None

def MockNode(*args, **kwargs):
    return Node(MockApp(), *args, **kwargs)

def test_node():
    root = MockNode()
    
    # move/position
    assert fcmp(root.position(), vec3(0))
    root.move(vec3(1,2,3))
    assert fcmp(root.position(), vec3(1,2,3))
    root.move(vec3(1,2,3))
    assert fcmp(root.position(), vec3(2,4,6))

    # reset
    root.position(vec3(0))
    assert fcmp(root.position(), vec3(0))

    # attach
    child = Node(MockApp())
    root.position(vec3(0))
    assert not root.children
    root.attach(child)
    assert root.children
    root.position(vec3(1,2,3))
    child.position(vec3(1))
    assert fcmp(child.position(WORLD), vec3(2,3,4))
    root.position(vec3(0))
    assert fcmp(child.position(WORLD), vec3(1))
    root.position(vec3(1))
    assert fcmp(child.position(WORLD), vec3(2))
    assert child.parent == root
    child.detach()
    assert child.parent == None
    assert fcmp(child.position(WORLD), vec3(1))
    root.attach(child)
    child.safe_detach()
    assert child in root.children
    root.logic(1) # will run scheduled safe detaches
    assert child not in root.children
