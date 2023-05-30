FROM livectf/livectf:quals-exploit

COPY libc.so.6 /libc.so.6
COPY solve-template.py /solve.py

WORKDIR /
CMD ["python3", "solve.py"]
