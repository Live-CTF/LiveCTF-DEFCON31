FROM livectf/livectf:quals-exploit

ARG REQUIRED_PACKAGES="python3 gdb"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${REQUIRED_PACKAGES} \
    && rm -rf /var/lib/apt/lists/*

COPY solve.py /
COPY extract.gdb /
WORKDIR /
CMD ["python3", "solve.py"]
