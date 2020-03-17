#!/usr/bin/env python

class Signal:
    def __init__(self):
        self.slots = {}
        self.meta = {}
    def ensure(self, func, context=''):
        if context not in self.slots:
            self.connect(func, context)
            return
        if func not in self.slots[context]:
            self.connect(func, context)
    def connect(self, func, context='', hidden=False):
        if context:
            self.meta[context] = {
                'hidden':  hidden
            }
        if context not in self.slots:
            self.slots[context] = []
        self.slots[context] += [func]
    def clear(self):
        self.slots = {}
    def disconnect(self, context):
        try:
            del self.slots[context]
            return True
        except KeyError:
            return False
    def __call__(self, *args, **kwargs):
        if not self.slots:
            return
        limit_context = kwargs.get('limit_context', None)
        brk = kwargs.get('allow_break', False)
        force_brk = kwargs.get('force_break', False)
        include_context = kwargs.get('include_context', False)
        items_copy = copy(self.slots.items())
        for ctx, funcs in items_copy:
            if not limit_context or ctx in limit_context:
                funcs_copy = copy(funcs)
                for func in funcs_copy:
                    r = None
                    if include_context:
                        r = func(ctx, *args)
                    else:
                        r = func(*args)
                    if brk and r:
                        return
                    if force_brk:
                        return

