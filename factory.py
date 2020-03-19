#!/usr/bin/env python

class Factory:
    def __init__(self):
        self.resolvers = []
        self.transform = None
    def register(self, pattern, Type):
        self.classes[pattern] = Type
    def register_transformer(self, func):
        self.transform = func
    def register_resolvers(self, funcs):
        for func in funcs:
            self.register_resolver(func)
    def register_resolver(self, func):
        """
        Resolver is a function to determine what type to build based on args
        Should return a Type or None
        """
        self.resolvers.append(func)
    def __call__(self, *args, **kwargs):
        Class = None
        for resolve in self.resolvers:
            Class = resolve(*args, **kwargs)
            if Class:
                break
        if self.transform:
            Class, args, kwargs = self.transform(Class, *args, **kwargs)
        assert Class # unable to resolve resource
        return Class(*args, **kwargs)

