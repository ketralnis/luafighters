#!/usr/bin/env python2.7

from setuptools import setup, find_packages, Extension

_executor = Extension('luafighters._executor',
                   define_macros = [('MAJOR_VERSION', '1'),
                                    ('MINOR_VERSION', '0')],
                   libraries = ['lua', 'm'],
                   library_dirs = ['/opt/local/lib'],
                   include_dirs = ['/opt/local/include', './c'],
                   sources = ['c/_executormodule.c'])

setup(
     name = 'luafighters',
     version = '1.0',
     description = 'Lua Fighters: Battle of the Luas',
     author = 'David King',
     author_email = 'dking@ketralnis.com',
     #url = 'https://docs.python.org/extending/building',
     long_description = "Players write Lua scripts to compete with each other",
     ext_modules = [_executor],
     packages=find_packages(),
     package_data={'luafighters': ['lua/*.lua']},
     zip_safe=False,
     include_package_data=True,
)
