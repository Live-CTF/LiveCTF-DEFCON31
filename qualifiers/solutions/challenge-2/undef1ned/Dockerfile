FROM livectf/livectf:quals-exploit

RUN pip install ptrlib
RUN apt update -y && apt install -y nasm
COPY solve-template.py /solve.py

WORKDIR /
CMD ["python3", "solve.py"]
