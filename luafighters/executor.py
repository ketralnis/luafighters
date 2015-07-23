from luafighters.utils import datafile
from luafighters._executor import execute as _execute

sandboxer = datafile('lua/sandbox.lua')

libraries = {}
for library in ['boardlib.lua']:
    libraries[library] = datafile('lua/%s'%library)

def execute(program, **env):
    ret = _execute(sandboxer,
                   {'user_code': program,
                    'libraries': libraries,
                    'env': env})
    return ret
