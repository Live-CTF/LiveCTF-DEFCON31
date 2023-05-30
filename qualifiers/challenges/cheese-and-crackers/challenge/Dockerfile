FROM livectf/livectf:quals-socat as base

FROM base as run

# Space-separated list of required packages
ARG REQUIRED_PACKAGES="python3 python3-pip curl tar xz-utils"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${REQUIRED_PACKAGES} && \
    rm -rf /var/lib/apt/lists/*

RUN curl -O https://ziglang.org/builds/zig-linux-x86_64-0.11.0-dev.1987+a2c6ecd6d.tar.xz
RUN tar xf zig-linux-x86_64-0.11.0-dev.1987+a2c6ecd6d.tar.xz
RUN mv zig-linux-x86_64-0.11.0-dev.1987+a2c6ecd6d /usr/local/zig

COPY generator/ /generator
COPY server/ /home/livectf/

RUN mkdir -p /handout 
COPY config.toml /handout
COPY server/run.sh /handout
COPY dist.Dockerfile /handout/Dockerfile
RUN cp /home/livectf/server.py /home/livectf/generator_dist.py /home/livectf/challenge /handout && \
      cd /home/livectf/ && \
      python3 dist.py && \
      cd / && \
      tar czf /handout.tar.gz /handout && \
      rm -rf /handout

COPY --chown=root:flag config.toml /home/livectf/.config.toml
RUN chmod 440 /home/livectf/.config.toml
