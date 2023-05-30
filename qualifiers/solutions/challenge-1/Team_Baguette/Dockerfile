FROM livectf/livectf:quals-exploit

COPY solve.py /solve.py
COPY get_rand.c /get_rand.c
RUN gcc get_rand.c -o get_rand

WORKDIR /
CMD ["python3", "solve.py"]
