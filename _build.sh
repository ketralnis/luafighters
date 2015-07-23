#!/bin/sh

set -e

rm -rf build

python ./setup.py build

cd ..

export PYTHONPATH=./luafighters/build/lib.macosx-10.4-x86_64-2.7

function maybe_debug {
    if false; then
        exec lldb $(which python) -- -m "$1"
    else
        exec python -m "$1"
    fi
}
