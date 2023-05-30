FROM livectf/livectf:quals-exploit

COPY challenge /
COPY libc.so.6 /
COPY solve.py /


WORKDIR /
CMD ["python3", "solve.py"]