#!/bin/bash

set -e

HANDOUT_FILES=(
    "./build/challenge"
    "./build/examples"
    "/lib/x86_64-linux-gnu/libc.so.6"
    "/lib64/ld-linux-x86-64.so.2"
)

mkdir -p build/examples
mkdir -p handout

# Build binaries
gcc src/challenge.c -gdwarf-3 -zrelro -znow -Wall -o build/challenge
nasm -f bin src/examples/fib.nasm -o build/examples/fib
nasm -f bin src/examples/tree.nasm -o build/examples/tree

# Copy required files to handout
for f in "${HANDOUT_FILES[@]}"; do
    cp -r "$f" handout/
done
