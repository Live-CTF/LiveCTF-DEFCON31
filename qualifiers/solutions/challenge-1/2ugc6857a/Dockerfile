FROM livectf/livectf:quals-exploit

COPY solve.py /solve.py

RUN pip install networkx

WORKDIR /
CMD ["python3", "solve.py"]
