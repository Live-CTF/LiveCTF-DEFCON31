#!/bin/sh
set -e
set -x

mkdir -p handouts/
CONTAINER_ID=$(docker create "livectf:$1")
docker cp "$CONTAINER_ID:/handout.tar.gz" "handouts/$1-handout.tar.gz"
docker rm "$CONTAINER_ID"
