FROM livectf/livectf:quals-exploit

RUN apt-get update
RUN apt-get -y install gdb binutils
COPY solve.py /solve.py

WORKDIR /
CMD ["python3", "solve.py"]
