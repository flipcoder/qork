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
import prompt_toolkit as pt
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

key_event = None
init = None
render = None
update = None
camera = None
view = None
gui = None
world = None
# _script_path = None
# data_path = "data"
# _script = None
# _on_run = None

# def set_camera(c = None):
#     global camera
#     camera = c


class ZeroMode(Core):
    def preload(self):
        global camera
        camera = self.camera = add(Camera())

    @classmethod
    def run(cls):
        try:
            mglw.run_window_config(cls)
        except KeyboardInterrupt:
            pass

    def __init__(self, **kwargs):
        global _script_path
        global init, render, update, camera, view, world, gui

        super().__init__(**kwargs)
        qork_app(self)
        self.script_path = _script_path
        d = path.join(path.dirname(path.dirname(self.script_path)), "data")
        self.data_path([".", d])

        self.bg_color = (0, 0, 0)
        self.shader = self.ctx.program(**SHADER_BASIC)
        # self.gui = Canvas(size=Lazy(lambda: self.size, [self.on_resize]))
        # self._gui = Canvas()

        self.preload()
        # "key_event", "mouse_event"
        # hooks = ["init", "render", "update", "script"]

        # self.camera.position = (0, 0, 0)

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
            if buflines[0].startswith("#!") and buflines[0].endswith("python"):
                print("Not a qork script. Run with python.")
                sys.exit(1)

        # extract globals
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

        def data_path(p=None):
            return self.data_path(p)

        app = qork_app()
        self.globe = {
            **qork.__dict__,
            **easy.__dict__,
            **util.__dict__,
            **decorators.__dict__,
            "QORK_SCRIPT": True,
            "glm": glm,
            "vec2": glm.vec2,
            "vec3": glm.vec3,
            "V2": glm.vec2,
            "V3": glm.vec3,
            "V": V,
            "init": init,
            "mouse": app.mouse,
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
            "update": update,
            "render": render,
            "world": world,
            "gui": gui,
            "camera": self.camera,
            # "overlap": qork.easy.overlap,
            # "add": qork.easy.add,
            "core": self,
            "data_path": data_path,
            "quit": lambda: sys.exit(0),  # temp
        }
        self.loc = {}
        # exec("import builtins", self.globe, self.loc)
        exec(buf, self.globe, self.loc)
        self.globe = {**self.globe, **self.loc}
        self.loc = {}

        # g = globals()
        # self.scope = {}
        # for name,var in loc.items():
        #     if name.startswith('__'):
        #         continue
        #     if not hasattr(g, name):
        #         # print('export', name)
        #         self.scope[name] = var
        #         # exec('global ' + name)
        # # for name,var in loc.items():
        # #     if name.startswith('__'):
        # #         continue
        # #     if not hasattr(g, name):
        # #         print('export', name)
        # #         g[name] = var

        def empty(*args):
            pass

        # for hook in hooks:
        #     try:
        #         globals()[hook] = self.globe[hook]
        #     except KeyError:
        #         globals()[hook] = empty

        self.update_hook = self.globe.get("update", None)
        self.render_hook = self.globe.get("render", None)
        self.init_hook = self.globe.get("init", None)

        self.prompt = asyncio.get_event_loop()
        self.prompt.create_task(self.run_prompt())

        if self.init_hook:
            self.init_hook()

    async def run_prompt(self):
        session = pt.PromptSession()
        while True:
            # with patch_stdout:
            result = None
            try:
                result = await session.prompt_async("> ")
            except:
                self.quit()
                break
            if result:
                try:
                    exec(result, self.globe, self.loc)
                    # exec('_prompt = ' + result + '; print(_prompt)', self.globe, self.loc)
                    # print(self.globe['prompt_']
                except Exception as e:
                    traceback.print_exc()

    def update(self, t):
        super().update(t)
        if self.update_hook:
            # TODO: make this faster
            exec("update(" + str(t) + ")", self.globe, self.loc)

        self.prompt.call_soon(self.prompt.stop)
        self.prompt.run_forever()

    def render(self, time, t):
        super().render(time, t)
        if render:
            render()


def main():
    global _script
    global _script_path
    console = True
    _script = sys.argv[-1]
    if len(sys.argv) == 1 or _script == __file__:
        _script = None
        _script_path = "."
    else:
        _script_path = _script
        sys.argv = sys.argv[:-1]
    ZeroMode.run()


if __name__ == "__main__":
    main()
