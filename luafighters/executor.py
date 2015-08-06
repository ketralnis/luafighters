from luafighters.utils import datafile
from luafighters._executor import _Executor

sandboxer = datafile('lua/sandbox.lua')

libraries = {}
for library in ['boardlib.lua']:
    libraries[library] = datafile('lua/%s'%library)


class Executor(_Executor):
    def execute(self, program, env):
        return super(Executor, self).execute(sandboxer,
                                             {'user_code': program,
                                              'libraries': libraries,
                                              'env': env})
