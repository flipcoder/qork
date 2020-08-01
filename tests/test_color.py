#!/usr/bin/env pytest

import sys
sys.path.append("..")
from qork.util import Color, fcmp
from glm import vec4

def test_color():
    col = Color()
    assert isinstance(col, Color)
    assert isinstance(col, vec4)
    assert fcmp(col, vec4(0,0,0,1))
    
def test_color_names():
    assert fcmp(Color('black'), vec4(0,0,0,1))
    assert fcmp(Color('white'), vec4(1,1,1,1))
    
    assert fcmp(Color('red'), vec4(1,0,0,1))
    # assert fcmp(Color('green'), vec4(0,1,0,1))
    assert fcmp(Color('blue'), vec4(0,0,1,1))
    
    assert fcmp(Color('black', 0.5), vec4(0,0,0,.5))

    assert Color(Color(Color('red'))) == Color('red') == 'red'
    assert 'green' == Color('green')
    assert 'red' != Color('blue')
    
    col = Color(Color('red').bgr)
    assert col == 'blue'

