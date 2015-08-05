#!/usr/bin/env python2.7

import os
import json

from setuptools import setup, find_packages, Extension

build_config = {}

if os.path.exists('build.conf'):
    with open('build.conf') as f:
        build_config = json.loads(f.read())

LUA_LIB = build_config.get('lua_lib', 'lua5.2')
INCLUDE_DIRS = build_config.get('include_dirs', []) + [
    '/opt/local/include',
    '/usr/include/lua5.2',
    './c'
]
LIBRARY_DIRS = build_config.get('library_dirs', []) + [
    '/opt/local/lib',
]

_executor = Extension('luafighters._executor',
                      define_macros=[('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
                      libraries=[LUA_LIB, 'm'],
                      library_dirs=LIBRARY_DIRS,
                      include_dirs=INCLUDE_DIRS,
                      sources=['c/_executormodule.c'],
                      extra_compile_args=['-std=c99'],
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
