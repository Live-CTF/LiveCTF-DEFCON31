
all: docker_challenge_api docker_exploit_builder docker_exploit_runner

local:
	docker volume create --name livectf_credentials
	DOCKER_BUILDKIT=1 docker-compose -f deploy/docker/docker-compose-local.yml up --build

build:
	DOCKER_BUILDKIT=1 docker-compose -f deploy/docker/docker-compose-build.yml build

push:
	DOCKER_BUILDKIT=1 docker-compose -f deploy/docker/docker-compose-build.yml push

local_scale:
	docker volume create --name livectf_credentials
	DOCKER_BUILDKIT=1 docker-compose -f deploy/docker/docker-compose-local.yml up --build --scale livectf_runner=3 --scale livectf_builder=3

local_clean:
	DOCKER_BUILDKIT=1 docker-compose -f deploy/docker/docker-compose-local.yml down --volumes
	docker volume rm livectf_credentials

celery_monitor:
	celery --broker=amqp://guest:guest@localhost:8081// flower

docker_challenge_api:
	DOCKER_BUILDKIT=1 docker build -t livectf_api -f deploy/docker/challenge-api.Dockerfile .

docker_exploit_builder:
	DOCKER_BUILDKIT=1 docker build -t livectf_builder -f deploy/docker/exploit-builder.Dockerfile .

docker_exploit_runner:
	DOCKER_BUILDKIT=1 docker build -t livectf_runner -f deploy/docker/exploit-runner.Dockerfile .

.PHONY: docker_challenge_api docker_exploit_builder docker_exploit_runner local celery_monitor all
