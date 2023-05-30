FROM livectf/livectf:quals-nsjail

COPY challenge /home/livectf/

COPY --chown=root:flag config.toml /home/livectf/.config.toml
RUN chmod 440 /home/livectf/.config.toml
