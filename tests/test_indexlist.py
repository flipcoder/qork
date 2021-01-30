#!/usr/bin/env pytest
import pytest
import sys

sys.path.append("..")

from qork.indexlist import IndexList

def test_indexlist_basic():
    mylist = IndexList()
    assert mylist.add(1) == 0
    two = mylist.add(2)
    assert mylist.add(3) == 2
    
    assert two == 1 # two's ID is 1, since it starts at 0
    
    assert mylist.get(0) == 1
    assert mylist.get(two) == 2
    assert mylist.get(2) == 3
    
    assert mylist.remove(two)

    # next power of 2 (length) of 3 length is 4, so 4 is the size
    # 2 is also missing because it was removed by ID
    cmplist = [1, None, 3, None]
    print(mylist.container)
    for i, e in enumerate(mylist.container):
        assert cmplist[i] == (e.item if e else None)
    

