FROM livectf/livectf:quals-exploit

COPY exploit.py /solve.py
COPY challenge /challenge

WORKDIR /
CMD ["python3", "solve.py"]
