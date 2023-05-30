FROM livectf/livectf:quals-socat as base

FROM base as build

# Space-separated list of required packages
ARG REQUIRED_PACKAGES="build-essential libseccomp-dev nasm"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${REQUIRED_PACKAGES} && \
    rm -rf /var/lib/apt/lists/*

COPY build.sh /build.sh
COPY src/ /src/
RUN mkdir /build /handout
RUN cd / && chmod +x /build.sh && /build.sh
COPY run.sh /handout

COPY config.toml /handout/
COPY dist.Dockerfile /handout/Dockerfile
RUN tar -czf /handout.tar.gz /handout

FROM base as run

# Custom run.sh to write flag to a file
COPY run.sh /home/livectf/run.sh
COPY --from=build /build/challenge /home/livectf/
COPY --from=build /build/examples/ /home/livectf/examples
COPY --from=build /handout.tar.gz /handout.tar.gz
COPY --chown=root:flag config.toml /home/livectf/.config.toml
RUN chmod 440 /home/livectf/.config.toml
