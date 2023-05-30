#!/bin/bash

set -e

HANDOUT_FILES=(
    "./build/challenge"
    "/lib/x86_64-linux-gnu/libc.so.6"
    "/lib64/ld-linux-x86-64.so.2"
)

# Build binaries
mkdir -p build
gcc src/challenge.c -O0 -g -Wall -o build/challenge

# Copy required files to handout
mkdir -p handout
for f in ${HANDOUT_FILES[@]}; do
    cp $f handout/
done
