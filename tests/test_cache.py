#!/usr/bin/env pytest
import pytest
import sys
sys.path.append('..')

import qork
from qork.cache import *
from qork.factory import *
from qork.util import *

def increment(x):
    return x + 1

class MockResource:
    def __init__(self, data=None, *args, **kwargs):
        self.data = data
        self.args = args
        self.kwargs = kwargs

def mock_resolver(fn):
    """
    Resolver is a Factory function based on cache id (filename)
    """
    if fn.endswith('.png'):
        return MockResource
    return None

def mock_transformer(*args, **kwargs):
    """
    Inject userdata into MockResource ctor
    """
    return MockResource, (['data'] + list(args)), kwargs

def test_cache_resolver():
    cache = Cache()
    cache.register(mock_resolver)
    res = cache('test.png')
    assert type(res) == MockResource
    res = None
    with pytest.raises(FactoryException):
        res = cache('test.invalid')
    assert not res
    res = None
    
def test_cache_transformer():
    cache = Cache(mock_resolver)
    cache.register_transformer(mock_transformer)
    res = cache('test2.png')
    assert res.data == 'data'
    print(res.args)
    assert len(res.args) == 2 # self, data
    assert not res.kwargs

def test_cache_direct():
    cleans = Wrapper(0)
    cache = Cache(mock_resolver)
    res = MockResource()
    res.cleanup = lambda self=res, x=cleans: x.do(increment)
    # invalid fn should not trigger factory error
    cache.ensure('test.invalid', res)
    assert cache('test.invalid')
    
def test_cache_clear():
    cleans = Wrapper(0)
    cache = Cache()
    res = cache.ensure('test.png', MockResource())
    res.cleanup = lambda self=res, x=cleans: x.do(increment)
    assert cache('test.png')
    assert cleans() == 0
    cache.clear()
    assert cleans() == 1

def test_cache_clean():
    cleans = Wrapper(0)
    cache = Cache()
    res = cache.ensure('test.png', MockResource())
    res.cleanup = lambda self=res, x=cleans: x.do(increment)
    assert cache.has('test.png')
    assert cleans() == 0
    assert res._count == 1
    cache.clean()
    assert res._count == 1
    assert cleans() == 0 # should not clean
    res.deref()
    assert res._count == 0
    count, remaining = cache.clean()
    assert cleans() == 1
    assert count == 1
    assert remaining == 0

