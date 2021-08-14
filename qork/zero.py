#!/usr/bin/python
import sys, os

try:
    import qork
except ModuleNotFoundError:
    sys.path.append(".")
    sys.path.append("..")
    import qork

QORK_PATH = os.path.dirname(os.path.abspath(__file__))

# sys.path.append(os.path.join(QORK_PATH, '../lib/pythonic-reactive/'))
# import pythonic_reactive

import traceback
import asyncio

from qork import *
from qork import easy
# from qork.easy import *
from qork.util import *
from qork.console import *
from os import path
from asyncio import sleep, create_task

# import console_toolkit as pt
# from console_toolkit import PromptSession
# from console_toolkit.patch_stdout import patch_stdout
from ptpython.repl import embed
import openal


class ZeroMode(Core):
    def preload(self):
        pass

    @classmethod
    def run(cls, title, script, script_path, use_terminal):
        return Core.run(cls, title, script, script_path, use_terminal)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        _script = self._script

        qork_app(self)
        self.terminal_stopped = False
        self._terminal = None

        pths = []
        if self.script_path:
            pths.append(path.dirname(self.script_path))
            pths.append(path.join(path.dirname(path.dirname(self.script_path)), "data"))
        else:
            self.script_path = os.getcwd()
            pths.append(self.script_path)
            pths.append(path.join(self.script_path, "data"))
        self.data_paths(pths)

        self.bg_color = (0, 0, 0)
        # self.shader = self.ctx.program(**SHADER_BASIC)
        self.shader = self.cache("SHADER", lambda: Shader(self, defs={"fog": False}))
        self.mvp_uniform = self.shader.program["ModelViewProjection"]
        # self.gui = Canvas(size=Lazy(lambda: self.size, [self.on_resize]))
        # self._gui = Canvas()

        self.preload()
        # "key_event", "mouse_event"
        # hooks = ["init", "render", "update", "script"]

        # self.cam.position = (0, 0, 0)

        if _script:
            with open(_script) as scriptfile:
                buf = scriptfile.read()
        else:
            buf = ""
        # for func in ['init','render','update','key_event']:
        #     buf = 'global '+func+'\n' + buf
        oldbuf = copy(buf)

        buflines = oldbuf.split("\n")
        if buflines:
            shebang = buflines[0].strip()
            if shebang.startswith("#!") and not shebang.endswith("qork"):
                print("Not a qork script. Run with python.")
                sys.exit(1)

        # [HACK] Extract globals
        for line in buflines:
            if not line.startswith(" ") and not line.startswith("\t"):
                tok = line.split(" ")
                if not tok:
                    continue
                lentok = len(tok)
                word = tok[0]
                if word.startswith("#"):  # comment
                    continue
                elif word == "def" or word == "class":
                    if tok[1].endswith(":"):
                        tok[1] = tok[1][:-1]
                    buf = "global " + tok[1].split("(")[0] + "\n" + buf
                # elif word == "import":
                #     pass
                elif word == "from":
                    if tok[2] == "import":
                        for t in tok[3:]:
                            if t[-1] == ",":
                                t = t[:-1]
                            # print('global', t)
                            buf = "global " + t + "\n" + buf
                elif "=" in word:
                    var = tok[0].split("=")[0]
                    if var[-1] in "+-%:|&^":
                        continue
                    if "." in var:
                        continue
                    if var.endswith("]"):  # array
                        continue
                    if "(" not in var:
                        buf = "global " + var + "\n" + buf
                elif lentok >= 2 and tok[1] == "=":
                    if "." in tok[0]:
                        continue
                    if tok[0].endswith("]"):  # array
                        continue
                    buf = "global " + word + "\n" + buf
                elif (
                    lentok >= 2
                    and len(tok[1]) > 1
                    and tok[1][0] == "="
                    and tok[1][1] != "="
                ):
                    buf = "global " + word + "\n" + buf

        app = qork_app()
        self.terminal_called = False
        # camera = self.camera
        # scene = self.scene

        self._init()
        # removed canvas and backdrop from here (added to State)
        self.canvas = self.app.canvas
        self.backdrop = self.app.backdrop

        # TODO: add signal on resize

        # inject qork types and methods into Q namespace?

        self.globe = {
            # "__builtins__": None,
            # "__builtins__": __builtins__,
            # "__loader__": __loader__,
            # "__file__": self.script_path,
            **qork.__dict__,
            # **easy.__dict__,
            **util.__dict__,
            **math.__dict__,
            **decorators.__dict__,
            "QORK_SCRIPT": True,
            "glm": glm,
            "vec2": glm.vec2,
            "vec3": glm.vec3,
            "V2": glm.vec2,
            "V3": glm.vec3,
            "V": V,
            # "RV": Rvec,
            "app": app,
            "KEY": app.wnd.keys,
        }
        
        self.q_funcs = {
            # "when": app.when,
            "every": app.when.every,
            "once": app.when.once,
            # "after": app.when.once,
            # "init": init,
            # "mouse_pos": app.mouse_pos,
            "hold_click": app.hold_click,
            "click": app.click,
            "unclick": app.unclick,
            "mouse_buttons": app.get_mouse_buttons,
            "mouse_buttons_pressed": app.get_mouse_buttons_pressed,
            "mouse_buttons_released": app.get_mouse_buttons_released,
            "key": app.get_key,
            "key_pressed": app.get_key_pressed,
            "key_released": app.get_key_released,
            "keys": app.get_keys,
            "keys_pressed": app.get_keys_pressed,
            "keys_released": app.get_keys_released,
            # "update": update,
            # "render": render,
            # "scene": self.scene,
            # "backdrop": self.backdrop,
            # "gui": self.gui,
            "terminal": self.terminal,
            # "console": self.console,
            # "backdrop": self.backdrop,
            # "canvas": self.canvas,
            # "camera": self.camera,
            # "data_paths": self._data_paths,
            "data_path": self.data_path,
            "quit": app.quit,
        }
        
        # add all easy mode functions to Q namespace
        for k,v in easy.funcs.items():
            # if k not in self.q_funcs:
            self.q_funcs[k] = v

        # class hashabledict(dict):
        #     def __hash__(self):
        #         return hash(tuple(sorted(self.items())))

        # q_obj = hashabledict({
        #     **self.q_funcs
        # })

        # populate Q namespace with q_funcs functions
        class Q:
            @property
            def app(self): return app

            @property
            def when(self): return app.when
            
            @property
            def mouse_pos(self): return app.mouse_pos
            
            @property
            def scene(self): return app.state_scene
            
            @property
            def backdrop(self): return app.state_backdrop
            
            @property
            def data_paths(self): return app.data_paths
            
            @property
            def canvas(self): return app.state_canvas

            @property
            def scale(self): return app.scale
            
            @property
            def camera(self): return app.state_camera

            @property
            def states(self): return app.states

        self.Q = Q()
            
        for k,v in self.q_funcs.items():
            if callable(v):
                # print(k, v)
                try:
                    getattr(Q, k)
                except AttributeError:
                    setattr(Q, k, v)
                    # setattr(Q, k, lambda *a, _v=v, **kw: _v(*a,**kw))
            else:
                assert False # Q attribute not callable

        # if USE_Q:
        self.globe = {
            **self.globe,
            "Q": self.Q,
        }
        # else:
        #     self.globe = {
        #         **self.globe,
        #         self.q_funcs
        #     }


        # additional vars for code golfing (optional in the future)
        # self.golf()

        if self.golfing:
            self.globe = {
                **self.globe,
                "A": app.add,
                "B": Box,
                # "C": app.camera,
                "F": easy.find,
                "F1": easy.find_one,
                # "V": already used
                # "N": Node
                "P": app.play,
                "R": app.remove,
                "RV": Rvec,
                "S": util.sint,
                "C": util.cost,
                "T": util.tant,
                # Q, V, already taken
            }

        self.loc = {}
        exec(buf, self.globe, self.loc)
        # builtins = self.globe['__builtins__']
        # self.globe['__builtins__'] = {**builtins, **self.loc}
        self.globe = {**self.globe, **self.loc}
        # self.loc = {}
        # print(self.loc)

        # TODO: count number of args for update() and do fixed fps if empty
        self.update_hook = self.globe.get("update", None) or self.globe.get("U", None)
        # self.render_hook = self.globe.get("render", None)
        self.init_hook = self.globe.get("init", None)

        self.script_hook = self.globe.get("script", None)

        if not self.terminal_called:
            self.terminal(self._use_terminal)

        # self.connections += self.states.on_change.connect(self.state_change)

        if self.init_hook:
            self.init_hook()

        # self.partitioner.refresh()

        if self.script_hook and self.script_hook is not qork.script:
            self.script_func = Script(self.script_hook)
        else:
            self.script_func = None

    # def _run_mode_script(self, fn, state):
    #     pass

    @property
    def _sf(self):
        """Shorted name for script_func, see ZeroMode.update()"""
        return self.script_func

    def terminal(self, b):
        self.terminal_called = True
        if b:
            self._terminal = asyncio.get_event_loop()
            self._terminal.create_task(self.run_terminal())
        else:
            self._terminal = None

    # def state_change(self):
    #     state = self.states.state or self
    #     self.globe["scene"] = state.scene
    #     self.globe["camera"] = state.camera

    @asyncio.coroutine
    def run_terminal(self):
        yield from embed(self.globe, return_asyncio_coroutine=True, patch_stdout=True)

        # session = pt.PromptSession()
        # while True:
        #     result = None
        #     try:
        #         result = await session.console_async("> ")
        #     except:
        #         self.quit()
        #         break
        #     if result:
        #         try:
        #             exec(result, self.globe, self.loc)
        #         except Exception as e:
        #             traceback.print_exc()

    def update(self, dt):
        super().update(dt)

        if self.update_hook:
            # self.update_hook(dt) # doesn't load globals correctly
            exec("update(" + str(dt) + ")", self.globe, self.loc)

        if self.script_func:
            # sf = script_func shortened
            exec("Q.app._sf(" + str(dt) + ")", self.globe, self.loc)

        if self._terminal:
            self._terminal.call_soon(self._terminal.stop)
            self._terminal.run_forever()

    def render(self, time, t):
        super().render(time, t)
        # if self.render_hook:
        #     self.render()

    def stop(self):
        if self._terminal and not self.terminal_stopped:
            self._terminal.call_soon(self.console.stop)
            self.terminal_stopped = True

    def __del__(self):
        self.stop()


def main():
    use_terminal = True
    args = sys.argv
    cut_args = []
    script = None
    script_path = None
    while True:

        good = 0
        try:  # remove flags, eg. '--blah'
            if args[-1].startswith("-"):
                cut_args = args[-1:]
                args = args[:-1]
            else:
                good += 1
        except IndexError:
            good += 1
            pass

        try:  # remove kwargs, eg '--vsync off'
            if args[-2].startswith("-"):
                cut_args += args[-2:]
                args = args[:-2]
            else:
                good += 1
        except IndexError:
            good += 1
        if good >= 2:
            break

    script = args[-1]
    if len(args) == 1 or script == __file__:
        script = None
        script_path = None
        use_terminal = True
    else:
        script_path = script
        use_terminal = False
        sys.argv = args[:-1] + cut_args

    ZeroMode.run("qork", script, script_path, use_terminal=use_terminal)


if __name__ == "__main__":
    try:
        Core.sys_start()
        main()
    except Exception:
        Core.sys_stop()
        raise
    Core.sys_stop()
