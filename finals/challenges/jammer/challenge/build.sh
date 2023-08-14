#!/bin/bash

set -e

HANDOUT_FILES=(
    "/lib/x86_64-linux-gnu/libc.so.6"
    "/lib64/ld-linux-x86-64.so.2"
)

mkdir -p handout

# Build binary
gcc src/*.c \
    -Wall -fno-stack-protector -no-pie -z execstack -Wl,-z,norelro \
    -o handout/challenge

# Copy required files to handout
for f in ${HANDOUT_FILES[@]}; do
    cp $f handout/
done
