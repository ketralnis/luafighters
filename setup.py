#!/usr/bin/env python2.7

from distutils.core import setup, Extension

helloc = Extension('luafighters.helloc',
                   define_macros = [('MAJOR_VERSION', '1'),
                                    ('MINOR_VERSION', '0')],
                   libraries = ['lua'],
                   library_dirs = ['/opt/local/lib'],
                   include_dirs = ['/opt/local/include', './c'],
                   sources = ['c/hellocmodule.c'])

setup(name = 'Lua Fighters',
      version = '1.0',
      description = 'Lua Fighters: Battle of the Luas',
      author = 'David King',
      author_email = 'dking@ketralnis.com',
      #url = 'https://docs.python.org/extending/building',
      long_description = '''Players write Lua scripts to compete with eachother''',
      ext_modules = [helloc],
      packages=['luafighters'])
