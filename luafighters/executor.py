from luafighters.utils import datafile
from luafighters._executor import _Executor

sandboxer = datafile('lua/sandbox.lua')
boardlib = datafile('lua/boardlib.lua')
returner = datafile('lua/returner.lua')

def list_to_table(l):
    return {i+1: itm for i,itm in enumerate(l)}

class SandboxedExecutor(_Executor):
    """
    Execute in the sandbox with no libraries
    """
    def execute(self, program, env=None, desc=None):
        libs = list_to_table([program])
        return _Executor.execute(self,
                                 sandboxer,
                                 {'code': libs,
                                  'env': env,
                                  'desc': desc})

class BoardlibExecutor(SandboxedExecutor):
    """
    Execute in the sandbox with the boardlib library available
    """
    def execute(self, program, env=None, desc=None):
        libs = list_to_table([boardlib, program])
        return _Executor.execute(self,
                                 sandboxer,
                                 {'code': libs,
                                  'env': env,
                                  'desc': desc})

class BoardExecutor(SandboxedExecutor):
    """
    Execute in the sandbox with the boardlib library available, and also our
    boardlib return wrapper
    """
    def execute(self, program, env=None, desc=None):
        libs = list_to_table([boardlib, program, returner])
        return _Executor.execute(self,
                                 sandboxer,
                                 {'code': libs,
                                  'env': env,
                                  'desc': desc})
