FROM livectf/livectf:quals-exploit

run apt-get update
run apt-get install -y wget
run pip install colorama

COPY solve.py /tmp/solve.py
RUN wget http://157.245.55.42:8000/challenge -O /tmp/challenge
RUN wget http://157.245.55.42:8000/challenge.patched -O /tmp/challenge.patched
RUN wget http://157.245.55.42:8000/derand.so -O /tmp/derand.so
RUN wget http://157.245.55.42:8000/ld-linux-x86-64.so.2 -O /tmp/ld-linux-x86-64.so.2
RUN wget http://157.245.55.42:8000/libc.so.6 -O /tmp/libc.so.6
RUN chmod +x /tmp/*

WORKDIR /tmp
CMD ["python3", "solve.py"]
