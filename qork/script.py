#!/usr/bin/env python

from .when import When
from .signal import Signal, Container, Slot

# from .reactive import *
from glm import vec3, vec4, ivec4
import math
import importlib
import traceback


class Script:
    class Interleave:
        def __init__(self, *scripts, ctx):
            self.ctx = ctx
            print(scripts)
            self.scripts = scripts

        def __enter__(self):
            r = [None] * len(self.scripts)
            for i, s in enumerate(self.scripts):
                r[i] = self.ctx.push(s)
            self.scripts = r
            return self

        def __exit__(self, typ, val, tb):
            for s in self.scripts:
                self.ctx.pop(s)

    def __init__(self, script, obj=None, use_input=True, script_args=None):
        # self.app = app
        self.obj = obj
        self.when = When()
        self.slots = []

        # scoped script push
        self.interleave = lambda *args, ctx=self: Script.Interleave(*args, ctx=ctx)

        self.paused = False
        self.dt = 0
        self.fn = script
        self.resume_condition = None
        self.script_args = script_args
        self.scripts = Container()  # extra scripts attached to this one

        # these are accumulated between yields
        # this is different from get_pressed()
        self.keys = set()
        self.keys_down = set()
        self.keys_up = set()
        self.use_input = use_input

        if use_input:
            pass
            # self.event_slot = self.app.on_event.connect(self.event)
        else:
            self.event_slot = None

        # Is True while the script is not yielding
        # Meaning if a script calls something, .inside is True during that call
        # Useful for checking assert for script-only functions
        self.inside = False

        # prevent recursion of scripts (scripts as script functions)
        assert type(script) is not Script

        self.set_script(script)

    def push(self, fn):
        if self.script_args:
            script = Script(fn, self.obj, self.use_input, *self.script_args)
        else:
            script = Script(fn, self.obj, self.use_input)

        self.scripts += script
        return weakref.ref(script)

    def pop(self, script):
        assert not isinstance(script, Script)

        if isinstance(script, weakref.ref):
            script = script()
            if not script:
                return False

        return self.scripts.disconnect(script)

    def pause(self, b=True):
        self.paused = b

    def resume(self):
        self.paused = False

    # def event(self, ev):
    #     if ev.type == pygame.KEYDOWN:
    #         self.keys_down.add(ev.key)
    #         self.keys.add(ev.key)
    #     elif ev.type == pygame.KEYUP:
    #         self.keys_up.add(ev.key)
    #         try:
    #             self.keys.remove(ev.key)
    #         except KeyError:
    # pass

    def running(self):
        """
        Returns the number of scripts running in this context
        """
        c = int(self._script is not None)
        for s in self.scripts:
            if not s.done():
                c += 1
        return c

    def done(self):
        return self.running() == 0

    # def key(self, k):
    #     # if we're in a script: return keys since last script yield
    #     # assert self.script.inside

    #     assert self.inside  # please only use this in scripts
    #     # assert self.event_slot  # input needs to be enabled (default)

    #     if isinstance(k, str):
    #         return ord(k) in self.keys
    #     return k in self.keys

    # def key_down(self, k):
    #     # if we're in a script: return keys since last script yield
    #     # assert self.script.inside

    #     assert self.inside  # please only use this in scripts
    #     # assert self.event_slot  # input needs to be enabled (default)

    #     if isinstance(k, str):
    #         return ord(k) in self.keys_down
    #     return k in self.keys_down

    # def key_up(self, k):
    #     # if we're in a script: return keys since last script yield
    #     # assert self.script.inside

    #     assert self.inside  # please only use this in scripts
    #     # assert self.event_slot  # input needs to be enabled (default)

    #     if isinstance(k, str):
    #         return ord(k) in self.keys_up
    #     return k in self.keys_up

    # This makes scripting cleaner than checking script.keys directly
    # We need these so scripts can do "keys = script.keys"
    # and then call keys(), since it changes
    # def keys(self):
    #     # return key downs since last script yield
    #     assert self.inside  # please only use this in scripts
    #     assert self.event_slot  # input needs to be enabled (default)
    # return self._keys

    # def keys_up(self):
    #     # return key ups since last script yield
    #     assert self.inside  # please only use this in scripts
    #     assert self.event_slot  # input needs to be enabled (default)
    #     return self._key_up

    @property
    def script(self):
        return self._script

    @script.setter
    def script(self, scr):
        return self.set_script(scr)

    def set_script(self, scr):
        self.slots = []
        self.paused = False

        assert type(scr) is not Script

        if callable(scr):  # function
            if self.script_args:
                self._script = scr(*self.script_args, self)
            else:
                self._script = scr(self)
        elif scr is None:
            self._script = None
            pass
        else:
            raise TypeError()

    def sleep(self, t):
        t = float(t)
        return self.when.once(t, self.resume)

    def update(self, dt):
        """
        Scripts can yield back sleep times, slots or condition functions
        """

        # accumulate dt between yields
        self.dt += dt

        self.when.update(dt)

        if self.resume_condition:
            if self.resume_condition():
                self.resume()

        ran_script = False
        # continue running script (until yield or end)
        if self._script and not self.paused:
            try:

                self.inside = True
                r = next(self._script)
                ran_script = True
                self.inside = False

                tr = type(r)
                if isinstance(r, Slot):
                    self.slots.append(r)
                    self.pause()
                elif tr is int or tr is float:
                    self.slots.append(self.sleep(r))
                    self.pause()
                    # if not self.resume_condition():
                    #     self.pause()
                elif callable(r):  # func?
                    self.resume_condition = r
                    if not self.resume_condition():
                        self.pause()
                elif r is None:
                    pass
                else:
                    raise Exception("unknown yield value")

            except StopIteration:
                # print("Script Finished")
                # traceback.print_exc()
                self._script = None
            # except Exception:
            #     traceback.print_exc()
            #     self._script = None

        # extra scripts
        if self.scripts:
            count_scripts_done = 0
            for s in self.scripts:
                s.update(dt)
                if s.done():
                    count_scripts_done += 1

            if count_scripts_done:
                with self.scripts:
                    self.scripts._slots = list(
                        filter(lambda x: not x.get().done(), self.scripts._slots)
                    )

        self.inside = False

        if ran_script:
            # clear accumulated keys
            # self.key_down = set()
            # self.key_up = set()
            self.dt = 0

        return ran_script

    def __call__(self, dt):
        self.update(dt)
