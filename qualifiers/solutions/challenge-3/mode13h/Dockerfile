FROM livectf/livectf:quals-exploit

COPY solve.py /solve.py
COPY libc.so.6 /

WORKDIR /
CMD ["python3", "solve.py"]
