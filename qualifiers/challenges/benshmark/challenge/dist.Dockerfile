FROM livectf/livectf:quals-socat

COPY challenge /home/livectf/
COPY examples /home/livectf/
COPY run.sh /home/livectf/

COPY --chown=root:flag config.toml /home/livectf/.config.toml
RUN chmod 440 /home/livectf/.config.toml
