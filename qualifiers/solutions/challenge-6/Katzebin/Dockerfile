FROM livectf/livectf:quals-exploit
RUN apt-get update
RUN apt-get install -y gdb
# COPY solve-template.py /solve.py
COPY solve.py /solve.py

WORKDIR /
CMD ["python3", "solve.py"]
