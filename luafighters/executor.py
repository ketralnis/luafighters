from luafighters.utils import datafile
from luafighters._executor import execute as _execute

sandboxer = open(datafile('lua/sandbox.lua')).read()

libraries = {}
for library in ['boardlib.lua']:
    libraries[library] = open(datafile('lua/%s'%library)).read()

def execute(program, **env):
    ret = _execute(sandboxer,
                   {'user_code': program,
                    'libraries': libraries,
                    'env': env})
    return ret
