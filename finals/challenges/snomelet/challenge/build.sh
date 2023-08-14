#!/bin/bash

set -e

HANDOUT_FILES=(
    "./src/challenge.py"
)


mkdir -p handout

# Copy required files to handout
for f in ${HANDOUT_FILES[@]}; do
    cp $f handout/
done
