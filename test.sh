#!/bin/sh

set -e

del build||true

python ./setup.py build

find build

cd ..

export PYTHONPATH=./luafighters/build/lib.macosx-10.4-x86_64-2.7

python -m luafighters.hellopython
