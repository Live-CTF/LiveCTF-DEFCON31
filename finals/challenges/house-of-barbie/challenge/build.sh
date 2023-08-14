#!/bin/bash

set -e

HANDOUT_FILES=(
    "./build/challenge"
    "/lib/x86_64-linux-gnu/libc.so.6"
    "/lib64/ld-linux-x86-64.so.2"
)

mkdir -p build handout

# Build binaries
gcc src/alloc.h src/alloc.c src/challenge.c -Wall -Wl,-z,norelro -o build/challenge -fno-pie -no-pie

# Copy required files to handout
for f in ${HANDOUT_FILES[@]}; do
    cp $f handout/
done
