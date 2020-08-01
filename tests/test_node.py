#!/usr/bin/env pytest
import pytest
import sys

sys.path.append("..")

from glm import vec3
from qork.util import *
from qork.node import Node
from qork.corebase import CoreBase
from qork.util import walk


def test_node():
    world = Node()

    # move/position
    assert fcmp(world.position, vec3(0))
    world.move(vec3(1, 2, 3))
    assert fcmp(world.position, vec3(1, 2, 3))
    world.move(vec3(1, 2, 3))
    assert fcmp(world.position, vec3(2, 4, 6))

    # reset
    world.pos = vec3(0)
    assert fcmp(world.position, vec3(0))

    # attach
    child = Node()
    world.position = vec3(0)
    assert not world.children
    world.attach(child)
    world.position = (1, 2, 3)
    child.position = vec3(1)
    assert fcmp(child.world_pos, vec3(2, 3, 4))
    world.position = vec3(0)
    assert fcmp(child.world_pos, vec3(1))
    world.position = vec3(1)
    assert fcmp(child.world_pos, vec3(2))
    assert child.parent == world
    child.detach()
    assert child.parent is None
    assert fcmp(child.world_pos, vec3(1))
    world.attach(child)
    world.children._blocked += 1
    child.detach()
    world.children._blocked -= 1
    assert child in world
    assert world.children._blocked == 0
    world.children.refresh()
    assert child not in world


def test_node_velocity():
    world = Node()
    world.velocity = (1, 2, 3)  # use tuple
    assert fcmp(world.position, vec3(0))
    world.update(1)
    assert fcmp(world.position, vec3(1, 2, 3))
    assert fcmp(world.position, vec3(1, 2, 3))
    world.update(1)
    assert fcmp(world.position, vec3(2, 4, 6))


def test_node_walk():
    a = Node()
    b = a.add(5)
    assert len(a) == 5
    assert len(list(a.walk())) == 5


def test_node_find():
    a = Node()
    b = a.add("foo")
    c = a.add("bar")

    assert list(a.find("foo")) == [b]
    assert list(a.find("bar")) == [c]

    b.tag("baz")
    assert b.tags == set(["baz"])
    assert list(a.find("baz")) == []
    assert list(a.find("#baz")) == [b]
