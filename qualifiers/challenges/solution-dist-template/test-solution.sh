#!/bin/sh

CHALLENGE_NAME="CHALLENGE_NAME_PLACEHOLDER"

docker build -t "livectf_${CHALLENGE_NAME}" handout
docker build -t "livectf_${CHALLENGE_NAME}_exploit" exploit

docker network create --internal --driver bridge "livectf_${CHALLENGE_NAME}_network"
CHALLENGE_CONTAINER=$(docker run -d --rm --privileged --network "livectf_${CHALLENGE_NAME}_network" -e "FLAG=LiveCTF{test-flag}" --name "livectf_${CHALLENGE_NAME}" "livectf_${CHALLENGE_NAME}:latest")
docker run --rm --network "livectf_${CHALLENGE_NAME}_network" -it -e "HOST=livectf_${CHALLENGE_NAME}" --name "livectf_${CHALLENGE_NAME}_exploit" "livectf_${CHALLENGE_NAME}_exploit:latest"
docker stop "$CHALLENGE_CONTAINER"
docker network rm "livectf_${CHALLENGE_NAME}_network"
