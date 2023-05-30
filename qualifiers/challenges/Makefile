challenges: challenge-test-challenge \
			challenge-benshmark \
			challenge-cheese-and-crackers \
			challenge-ptrace-me-maybe \
			challenge-test-your-luck \
			challenge-what-a-maze-meant \
			challenge-dont-b-link

challenge-test-challenge:
	DOCKER_BUILDKIT=1 docker build -t livectf:quals-test-challenge test-challenge/challenge
	./extract-handout.sh quals-test-challenge

challenge-benshmark:
	DOCKER_BUILDKIT=1 docker build -t livectf:quals-benshmark benshmark/challenge
	./extract-handout.sh quals-benshmark

challenge-cheese-and-crackers:
	DOCKER_BUILDKIT=1 docker build -t livectf:quals-cheese-and-crackers cheese-and-crackers/challenge
	./extract-handout.sh quals-cheese-and-crackers

challenge-ptrace-me-maybe:
	DOCKER_BUILDKIT=1 docker build -t livectf:quals-ptrace-me-maybe ptrace-me-maybe/challenge
	./extract-handout.sh quals-ptrace-me-maybe

challenge-test-your-luck:
	DOCKER_BUILDKIT=1 docker build -t livectf:quals-test-your-luck test-your-luck/challenge
	./extract-handout.sh quals-test-your-luck

challenge-what-a-maze-meant:
	DOCKER_BUILDKIT=1 docker build -t livectf:quals-what-a-maze-meant what-a-maze-meant/challenge
	./extract-handout.sh quals-what-a-maze-meant

challenge-dont-b-link:
	DOCKER_BUILDKIT=1 docker build -t livectf:quals-dont-b-link dont-b-link/challenge
	./extract-handout.sh quals-dont-b-link

.PHONY: challenges \
		challenge-benshmark \
		challenge-cheese-and-crackers \
		challenge-ptrace-me-maybe \
		challenge-test-your-luck \
		challenge-what-a-maze-meant \
		challenge-dont-b-link
