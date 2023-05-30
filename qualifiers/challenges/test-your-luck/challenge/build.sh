#!/bin/bash

set -e

HANDOUT_FILES=(
    "./build/challenge"
)

# Build binaries
gcc -Wall -masm=intel src/syscall.S src/challenge.c -O2 -Wl,-z,norelro -fstack-protector-all -o build/challenge
python3 src/encrypt.py
strip -s build/challenge

# Copy required files to handout
for f in ${HANDOUT_FILES[@]}; do
    cp $f handout/
done
