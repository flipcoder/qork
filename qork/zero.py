#!/usr/bin/python
import sys

try:
    import qork
except ModuleNotFoundError:
    sys.path.append(".")
    sys.path.append("..")
    import qork

import traceback
import asyncio

from qork import *
from qork.easy import *
from qork.util import *
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
    def run(cls):
        try:
            mglw.run_window_config(cls)
        except KeyboardInterrupt:
            pass

    def __init__(self, **kwargs):
        global _script_path

        super().__init__(**kwargs)
        qork_app(self)
        self.script_path = _script_path
        pths = []
        if self.script_path:
            pths.append(path.join(path.dirname(self.script_path)))
            pths.append(path.join(path.dirname(path.dirname(self.script_path)), "data"))
        else:
            self.script_path = os.getcwd()
            pths.append(self.script_path)
            pths.append(path.join(self.script_path, "data"))
        self.data_paths(pths)

        self.bg_color = (0, 0, 0)
        self.shader = self.ctx.program(**SHADER_BASIC)
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

        # extract globals (hack!)
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
        self._console = None
        self.console_called = False
        self.globe = {
            **qork.__dict__,
            **easy.__dict__,
            **util.__dict__,
            **math.__dict__,
            **decorators.__dict__,
            "QORK_SCRIPT": True,
            "glm": glm,
            "vec2": glm.vec2,
            "vec3": glm.vec3,
            "V2": glm.vec2,
            "V3": glm.vec3,
            # "V": V,
            "RV": Rvec,
            "Q": app,
            "app": app,
            "when": app.when,
            "every": app.when.every,
            "once": app.when.once,
            # "after": app.when.once,
            # "init": init,
            "mouse_pos": app.mouse_pos,
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
            "KEY": app.wnd.keys,
            # "update": update,
            # "render": render,
            "scene": self.scene,
            # "gui": self.gui,
            "console": self.console,
            "camera": self.camera,
            "data_paths": self._data_paths,
            "data_path": self.data_path,
            "quit": app.quit,
        }

        # additional vars for code golfing (optional in the future)
        self.golf()

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
        self.globe = {**self.globe, **self.loc}
        self.loc = {}

        self.update_hook = self.globe.get("update", None) or self.globe.get("U", None)
        self.render_hook = self.globe.get("render", None)
        self.init_hook = self.globe.get("init", None)

        if not self.console_called:
            self.console(True) # console enabled by default
        
        self.connections += self.states.on_change.connect(self.state_change)

        if self.init_hook:
            self.init_hook()

        self.partitioner.refresh()

    def console(self, b):
        self.console_called = True
        if b:
            self._console = asyncio.get_event_loop()
            self._console.create_task(self.run_console())
        else:
            self._console = None
    
    def state_change(self):
        state = self.states.top() or self
        self.globe["scene"] = state.scene
        self.globe["camera"] = state.camera

    @asyncio.coroutine
    def run_console(self):
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
            # TODO: make this faster
            exec("update(" + str(dt) + ")", self.globe, self.loc)

        if self._console:
            self._console.call_soon(self._console.stop)
            self._console.run_forever()

    def render(self, time, t):
        super().render(time, t)
        # if self.render_hook:
        #     self.render()

    def __del__(self):
        if self._console:
            self._console.call_soon(self.console.stop)


def main():
    global _script
    global _script_path
    console = True
    args = sys.argv
    cut_args = []
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

    _script = args[-1]
    if len(args) == 1 or _script == __file__:
        _script = None
        _script_path = None
    else:
        _script_path = _script
        sys.argv = args[:-1] + cut_args
    ZeroMode.run()


if __name__ == "__main__":
    try:
        Core.sys_start()
        main()
    except Exception:
        Core.sys_stop()
        raise
    Core.sys_stop()
