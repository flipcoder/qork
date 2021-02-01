#!/usr/bin/python3

from .util import try_get
from .signal import Signal
from .reactive import Container
from dataclasses import dataclass


def next_power_of_two_ge(x):

    x = int(x)
    x -= 1
    for i in range(5):
        x |= x >> (1 << i)
    x += 1
    return x


class IndexList:
    @dataclass
    class Element:
        num: int = -1
        item: any = None
        on_remove: Signal = None

    def __init__(self):
        self.next_id = 0
        self.container = []  # (element, on_remove)
        self.sz = 0  # not container len, but actual num of non-Nones

    def ensure_length(self, length):
        lenct = len(self.container)
        if lenct < length:
            self.container += [None] * (length - lenct)

    def __iadd__(self, obj):
        self.add(obj)
        return self

    def __isub__(self, obj):
        if type(obj) is int:
            self.remove(obj)  # index
        else:
            self.remove(self.get_id(obj))
        return self

    def __len__(self):
        return self.sz

    def add(self, obj):
        while True:
            idx = self.next_id
            if idx >= len(self.container):
                self.ensure_length(next_power_of_two_ge(idx + 1))
            if try_get(self.container, idx, None) is None:
                self.container[idx] = IndexList.Element(idx, obj, Signal())
                self.next_id += 1
                self.sz += 1
                return idx
            self.next_id += 1

    def remove(self, idx):
        try:
            item = self.container[idx]
            if item is not None:
                item.on_remove()
        except IndexError:
            pass

        if item is not None:
            try:
                self.container[idx] = None
                self.sz -= 1
                return True
            except IndexError:
                return False
        else:
            return False

    def get(self, idx):
        """Get item using ID"""
        try:
            return self.container[idx].item
        except IndexError:
            return None

    def __index__(self, idx):
        r = self.container[idx].item
        if r is None:
            raise IndexError()
        return r

    def clear(self):
        for cb in self.container[:]:
            cb.on_remove()

        self.next_id = 0
        self.container = []
        self.sz = 0

    def on_remove(self, idx):
        """Get on_remove signal of item by item index"""
        return self.container[idx].on_remove

    def get_id(self, item):
        """Get ID of item"""
        for e in self.container:
            if e.item == item:
                return e.num

    def __iter__(self):
        return iter(self.container)

    def safe_iter(self):
        """Copy container and safely iterate it"""
        return iter(self.container[:])
