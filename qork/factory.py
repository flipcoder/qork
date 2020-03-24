#!/usr/bin/env python


class FactoryException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class Factory:
    def __init__(self, resolver=None, transformer=None):
        self.resolvers = [resolver] if resolver else []
        self.transform = [transformer] if transformer else []

    def register_transformer(self, func):
        """
        Register optional transform/normalizer function.
        Can be used to normalize filenames and
        add in additional parameters to Class ctor
        """
        if callable(func):
            self.transform.append(func)
        else:
            self.transform += func

    def register(self, func):
        """
        Resolver is a function to determine what type to build based on args
        Should return a Type or None
        """
        if callable(func):
            self.resolvers.append(func)
            return
        for f in func:
            self.register(f)

    def __call__(self, *args, **kwargs):
        Class = None
        if not self.resolvers:
            raise FactoryException(
                "Unable to resolve resource: '" + str((args, kwargs)) + "'"
            )
        for transform in self.transform:
            args, kwargs = transform(*args, **kwargs)
        for resolve in self.resolvers:
            Class, args, kwargs = resolve(*args, **kwargs)
            if Class:
                break  # success
        if not Class:
            raise FactoryException(
                "Unable to resolve resource: '" + str((args, kwargs)) + "'"
            )
        return Class(*args, **kwargs)
