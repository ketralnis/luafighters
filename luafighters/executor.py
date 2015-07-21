from luafighters.utils import datafile
from luafighters._executor import execute as _execute

sandboxer = open(datafile('lua/sandbox.lua')).read()

def execute(program, **env):
    ret = _execute(sandboxer,
                   {'user_code': program,
                    'env': env})
    return ret
