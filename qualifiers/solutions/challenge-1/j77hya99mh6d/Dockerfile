FROM livectf/livectf:quals-exploit

RUN pip3 install parse

COPY solve2.py /solve.py

WORKDIR /
CMD ["python3", "solve.py"]
