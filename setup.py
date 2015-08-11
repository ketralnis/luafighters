#!/usr/bin/env python2.7

import os
import json
import platform

from setuptools import setup, find_packages, Extension

build_config = {}

BUILDCONF = os.environ.get('LUAFIGHTERS_BUILDCONF', 'build.conf')

if os.path.exists(BUILDCONF):
    with open(BUILDCONF) as f:
        build_config = json.loads(f.read())

LUA_LIB = build_config.get('lua_lib', 'lua5.2')
INCLUDE_DIRS = build_config.get('include_dirs', [])
LIBRARY_DIRS = build_config.get('library_dirs', [])
EXTRA_COMPILE_ARGS = build_config.get('extra_compile_args', [])
EXTRA_LINK_ARGS = build_config.get('extra_link_args', [])

# if 'jit' in LUA_LIB and platform.system() == 'Darwin':
#     EXTRA_LINK_ARGS += ["-pagezero_size 10000", "-image_base 100000000"]

_executor = Extension('luafighters._executor',
                      define_macros=[('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
                      libraries=[LUA_LIB, 'm'],
                      library_dirs=LIBRARY_DIRS,
                      include_dirs=['./c'] + INCLUDE_DIRS,
                      sources=['c/_executormodule.c'],
                      extra_compile_args=['-std=c99'] + EXTRA_COMPILE_ARGS,
                      extra_link_args=EXTRA_LINK_ARGS,
                      )

setup(
    name='luafighters',
    version='1.0',
    description='Lua Fighters: Battle of the Luas',
    author='David King',
    author_email='dking@ketralnis.com',
    #url='https://docs.python.org/extending/building',
    long_description="Players write Lua scripts to compete with each other",
    ext_modules=[_executor],
    packages=find_packages(),
    package_data={'luafighters': ['lua/*.lua', 'static/*', 'mako/*']},
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'termcolor',
        'flask',
        'mako',
        'simplejson',
        'redis',
    ],
)
