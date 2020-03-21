#!/usr/bin/python
import sys
# if len(sys.argv)==0:
#     sys.argv = ['qork']
# sys.path.append('.')
# sys.path.append('..')
import qork
from qork import *
from qork.zero import *
from os import path

key_event = None
init = None
render = None
update = None
camera = None
view = None
gui = None
root = None
_script_path = None
data_path = 'data'
_script = None
_on_run = None

# def set_camera(c = None):
#     global camera
#     camera = c

class ZeroMode(Core):
    def preload(self):
        global camera
        camera = self.camera = add(Camera())
    
    def __init__(self, **_kwargs):
        global _script_path
        global init, render, update, camera, view, root, gui
        
        super().__init__(**_kwargs)
        qork_app(self)
        self._data_path = None
        self.script_path = _script_path
        d = path.join(path.dirname(path.dirname(self.script_path)),'data')
        self.data_path(d)
        
        bg_color = self.bg_color = (0,0,0)
        shader = self.shader = self.ctx.program(**SHADER_BASIC)
        
        root = self.root
        self.preload()
        hooks = ['init','render','update','key_event','mouse_event']
        
        with open(_script) as scriptfile:
            buf = scriptfile.read()
        # for func in ['init','render','update','key_event']:
        #     buf = 'global '+func+'\n' + buf
        oldbuf = copy(buf)

        buflines = oldbuf.split('\n')
        if buflines:
            if buflines[0].startswith('#!') and buflines[0].endswith('python'):
                print('Not a qork script. Run with python.')
                sys.exit(1)
        
        # extract globals
        for line in buflines:
            if not line.startswith(' ') and not line.startswith('\t'):
                tok = line.split(' ')
                if not tok:
                    continue
                lentok = len(tok)
                word = tok[0]
                if word.startswith('#'): # comment
                    continue
                elif word == 'def' or word=='class':
                    if tok[1].endswith(':'):
                        tok[1] = tok[1][:-1]
                    buf = 'global ' + tok[1].split('(')[0] + '\n' + buf
                elif '=' in word:
                    var = tok[0].split('=')[0]
                    if '.' in var:
                        continue
                    if var.endswith(']'): # array
                        continue
                    buf = 'global ' + var + '\n' + buf
                elif lentok>=2 and tok[1] == '=':
                    if '.' in tok[0]:
                        continue
                    if tok[0].endswith(']'): # array
                        continue
                    buf = 'global ' + word + '\n' + buf
                elif lentok>=2 and len(tok[1]) > 1 and tok[1][0]=='=' and tok[1][1] != '=':
                    buf = 'global ' + word + '\n' + buf
        
        def data_path(p=None):
            return self.data_path(p)
        
        globe = {
            **qork.__dict__,
            **zero.__dict__,
            'QORK_SCRIPT': True,
            'glm': glm,
            'vec2': glm.vec2,
            'vec3': glm.vec3,
            'init': init,
            'update': update,
            'render': render,
            'root': root,
            'camera': camera,
            'core': self,
            'data_path': data_path,
            'quit': lambda: sys.exit(0) # temp
        }
        loc = {}
        exec(buf, globe, loc)
        
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
        for hook in hooks: 
            try:
                globals()[hook] = globe[hook]
            except KeyError:
                globals()[hook] = empty

        # self.scope['update'] = update
        # self.scope['render'] = render
        
        if init:
            init()

    def key_event(self, key, action, modifiers):
        if key_event:
            key_event(key, action, modifiers)
    
    def update(self, t):
        super().update(t)
        # if logic:
        #     logic(t)
        if update:
            # update(t)
            # exec('update(t)')
            update(t)
            # g = {**(globals()), **{'t':t}}
            # exec('update(t)', g, self.scope)
        # exec(self._update, self._locals, self._globals)

    def render(self, time, t):
        super().render(time, t)
        if render:
            render()
        # if draw:
        #     draw()

def main():
    global _script
    global _script_path
    _script = sys.argv[-1]
    if len(sys.argv)==1 or _script == __file__:
        print('qork <script.py>')
        sys.exit(1)
    _script_path = sys.argv[-1]
    sys.argv = sys.argv[:-1]
    ZeroMode.run()
    
if __name__=='__main__':
    main()

