FROM livectf/livectf:quals-socat as base

# Space-separated list of required packages
ARG REQUIRED_PACKAGES="build-essential cmake python3"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${REQUIRED_PACKAGES} && \
    rm -rf /var/lib/apt/lists/*

FROM base as build

COPY src/server.py /build/
COPY src/server.py /handout/
COPY src/challenge /build/challenge
COPY src/challenge /handout/challenge
RUN chmod +x /build/challenge
RUN chmod +x /handout/challenge
RUN mkdir /build/src
RUN mkdir /handout/src
COPY src/src /build/src
COPY src/src /handout/src

COPY dist.Dockerfile /handout/Dockerfile
COPY config.toml /handout/
RUN tar -czf /handout.tar.gz /handout

FROM base as run

COPY --from=build /build/challenge /home/livectf/
COPY --from=build /build/server.py /home/livectf/
RUN mkdir /home/livectf/src
COPY --from=build /build/src /home/livectf/src
COPY --from=build /handout.tar.gz /handout.tar.gz
COPY --chown=root:flag config.toml /home/livectf/.config.toml
RUN chmod 440 /home/livectf/.config.toml
