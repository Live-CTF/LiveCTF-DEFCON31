FROM livectf/livectf:quals-exploit

RUN python3 -m pip install z3-solver
COPY solve.py /

WORKDIR /
CMD ["python3", "solve.py"]
