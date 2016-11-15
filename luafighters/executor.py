from lua_sandbox.executor import SandboxedExecutor

from luafighters.utils import datafile


class BoardExecutor(object):
    sandboxer = datafile('lua/sandbox.lua')
    boardlib = datafile('lua/boardlib.lua')

    def __init__(self, code):
        self.lua = SandboxedExecutor(name=self.__class__.__name__,
                                     max_memory=20*1024*1024,
                                     sandboxer=self.sandboxer,
                                     libs=[self.boardlib])
        self.fn = self.lua.sandboxed_load(code, desc='loaded')

    def execute(self, **env):
        for k, v in env.iteritems():
            self.lua.sandbox[k] = v

        with self.lua.limit_runtime(max_runtime=3.0):
            self.fn()

        ret = self.lua.sandbox['orders'].to_python()

        self.lua.sandbox['orders'] = {}

        return ret
