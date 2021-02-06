#!/usr/bin/env pytest
import pytest
import sys

sys.path.append("..")

import qork
from qork.cache import *
from qork.factory import *
from qork.util import *
import gc


def increment(x):
    return x + 1


class MockResource(Resource):
    def __init__(self, fn="", data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fn = fn
        self.data = data


def mock_resolver(*args, **kwargs):
    """
    Resolver is a Factory function based on cache id (filename)
    """
    fn = filename_from_args(args, kwargs)
    if fn.endswith(".png"):
        return MockResource, args, kwargs
    return None, None, None


def mock_transformer(*args, **kwargs):
    """
    Inject userdata into MockResource ctor
    """
    args = [args[0]] + ["data"] + list(args[1:])
    return args, kwargs


def test_cache_resolver():
    cache = Cache()
    cache.register(mock_resolver)
    res = cache("test.png")
    assert type(res) == MockResource
    res = None
    with pytest.raises(FactoryException):
        res = cache("test.invalid")
    assert not res
    res = None


def test_cache_transformer():
    cache = Cache(mock_resolver, mock_transformer)
    res = cache("test.png")
    assert res.fn == "test.png"
    assert res.data == "data"
    assert len(res.args) == 0
    assert not res.kwargs


def test_cache_direct():
    cleans = Wrapper(0)
    cache = Cache(mock_resolver)
    res = MockResource()
    res.__del__ = lambda self=res, x=cleans: x.do(increment)
    # invalid fn should not trigger factory error
    cache.ensure("test.invalid", res)
    assert cache("test.invalid")


# def test_cache_clear():
#     cleans = Wrapper(0)
#     cache = Cache()
#     res = cache.ensure('test.png', MockResource())
#     res.cleanup = lambda self=res, x=cleans: x.do(increment)
#     assert cache('test.png')
#     assert cleans() == 0
#     cache.clear() # clear forces resource cache to do call cleanup
#     assert cleans() == 1


def test_cache_clean():
    # cleans = Wrapper(0)
    cache = Cache()
    res = cache.ensure("test.png", MockResource())
    # res.__del__ = lambda self, x=cleans: x.do(increment)
    assert cache.has("test.png")
    # assert cleans() == 0
    assert cache.count("test.png") == 1
    cache.clean()
    assert cache.count("test.png") == 1
    # assert cleans() == 0  # should not clean
    res.deref()
    # assert res._count == 0
    # gc.collect()
    count, remaining = cache.clean()
    # assert cleans() == 1
    assert count == 1
    assert remaining == 0


# def test_cache_leak():
#     # cleans = Wrapper(0)
#     cache = Cache()
#     res = cache.ensure("test.png", MockResource())
#     # res.__del__ = lambda self=res, x=cleans: x.do(increment)
#     assert "test.png" in cache
#     cache.finish()
#     assert len(cache) == 0
    # assert cleans() == 0


# def test_cache_finish():
#     cleans = Wrapper(0)
#     cache = Cache()
#     res = cache.ensure("test.png", MockResource())
#     res.__del__ = lambda self=res, x=cleans: x.do(increment)
#     res.deref()
#     # gc.collect()
#     assert cleans() == 0
#     cache.finish()
#     assert cleans() == 1
