FROM livectf/livectf:quals-exploit

COPY solve.py /
COPY brute_force_seed /
COPY maze_solver.py /
COPY decode_description.py /

WORKDIR /
CMD ["python3", "solve.py"]
