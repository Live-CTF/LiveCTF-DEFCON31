#!/bin/sh
set -e
set -x

mkdir -p handouts/
CONTAINER_ID=$(docker create "livectf:$1")
docker cp "$CONTAINER_ID:/handout.tar.gz" "handouts/$1-handout.tar.gz"
docker rm "$CONTAINER_ID"

TEMP_DIR=$(mktemp -d)
cp "handouts/$1-handout.tar.gz" "$TEMP_DIR/$1-handout.tar.gz"
tar -C "$TEMP_DIR" -xf "$TEMP_DIR/$1-handout.tar.gz"
rm "$TEMP_DIR/$1-handout.tar.gz"
cp -r solution-dist-template/* "$TEMP_DIR"
sed -i "s/CHALLENGE_NAME_PLACEHOLDER/$1/" "$TEMP_DIR/test-solution.sh"
tar -czf "handouts/$1-handout.tar.gz" -C "$TEMP_DIR" .
rm -rf "$TEMP_DIR"
