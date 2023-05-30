FROM livectf/livectf:quals-socat

ARG REQUIRED_PACKAGES="build-essential cmake python3"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${REQUIRED_PACKAGES} \
    && rm -rf /var/lib/apt/lists/*

COPY server.py /home/livectf/
COPY challenge /home/livectf/
RUN mkdir src
COPY src /home/livectf/src

COPY --chown=root:flag config.toml /home/livectf/.config.toml
RUN chmod 440 /home/livectf/.config.toml
