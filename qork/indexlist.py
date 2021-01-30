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
        self.container = [] # (element, on_remove)
    def ensure_length(self, length):
        lenct = len(self.container)
        if lenct < length:
            self.container += [None] * (length - lenct)
    def add(self, obj):
        while True:
            idx = self.next_id
            if try_get(self.container, idx, None) is None:
                self.ensure_length(next_power_of_two_ge(idx + 1))
                self.container[idx] = IndexList.Element(idx, obj, Signal())
            self.next_id += 1
            return idx
    def remove(self, idx):
        try:
            item = self.container[idx]
            if item is not None:
                item.on_remove()
        except IndexError:
            pass
        
        try:
            self.container[idx] = None
            return True
        except IndexError:
            return False

    def get(self, idx):
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

    def on_remove(self, idx):
        return self.container[idx].on_remove

    def get_id(self, item):
        for e in self.container:
            if e.item == item:
                return e.num

