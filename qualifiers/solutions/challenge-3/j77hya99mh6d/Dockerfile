FROM livectf/livectf:quals-exploit

RUN pip3 install icecream pycryptodome

COPY solve-template.py /solve.py

WORKDIR /
CMD ["python3", "solve.py"]
