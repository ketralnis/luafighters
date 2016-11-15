#!/usr/bin/env python2.7

from setuptools import setup, find_packages

setup(
    name='luafighters',
    version='1.1',
    description='Lua Fighters: Battle of the Luas',
    author='David King',
    author_email='dking@ketralnis.com',
    #url='https://docs.python.org/extending/building',
    long_description="Players write Lua scripts to compete with each other",
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
        'lua_sandbox>=2.1.0',
        'flask_json',
    ],
    dependency_links=[
        'https://github.com/ketralnis/lua_sandbox/archive/v2.1.0.tar.gz#egg=lua_sandbox-2.1.0',
    ]
)
