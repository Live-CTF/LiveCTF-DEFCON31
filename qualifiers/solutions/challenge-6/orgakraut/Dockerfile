FROM livectf/livectf:quals-exploit

COPY exploit.py /solve.py
COPY solver.py /solver.py
# COPY challenge /challenge

WORKDIR /
CMD ["python3", "solve.py"]
