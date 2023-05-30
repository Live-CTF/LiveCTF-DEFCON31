FROM livectf/livectf:quals-exploit

COPY solve-template.py /solve.py
COPY libc.so.6 /libc.so.6

WORKDIR /
CMD ["python3", "solve.py"]
