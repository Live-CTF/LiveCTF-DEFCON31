FROM livectf/livectf:quals-socat

ARG REQUIRED_PACKAGES="python3"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${REQUIRED_PACKAGES} \
    && rm -rf /var/lib/apt/lists/*

COPY samples /home/livectf/samples
COPY challenge /home/livectf/
COPY server.py /home/livectf/
COPY run.sh /home/livectf/
COPY generator_dist.py /home/livectf/

COPY --chown=root:flag config.toml /home/livectf/.config.toml
RUN chmod 440 /home/livectf/.config.toml

ENV LOCAL=1
