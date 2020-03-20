#!/usr/bin/env python

class FactoryException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

class Factory:
    def __init__(self, resolver=None, transformer=None):
        self.resolvers = [resolver] if resolver else []
        self.transform = transformer if transformer else None
    def register_transformer(self, func):
        self.transform = func
    def register(self, func):
        """
        Resolver is a function to determine what type to build based on args
        Should return a Type or None
        """
        if callable(func):
            self.resolvers.append(func)
            return
        for func in funcs:
            self.register(func)
    def __call__(self, *args, **kwargs):
        Class = None
        if not self.resolvers:
            raise FactoryException("Unable to resolve resource: '" + str((args, kwargs)) +  "'")
        for resolve in self.resolvers:
            Class = resolve(*args, **kwargs)
            if Class:
                break
        if self.transform:
            Class, args, kwargs = self.transform(Class, *args, **kwargs)
        if not Class:
            raise FactoryException("Unable to resolve resource: '" + str((args, kwargs)) +  "'")
        return Class(*args, **kwargs)

