#!/bin/sh

set -e

del build||true

python ./setup.py build

find build

cd ..

export PYTHONPATH=./luafighters/build/lib.macosx-10.4-x86_64-2.7

if false; then
    exec lldb $(which python) -- -m luafighters.hellopython
else
    exec python -m luafighters.hellopython
fi
