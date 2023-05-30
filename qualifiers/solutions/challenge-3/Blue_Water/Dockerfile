FROM livectf/livectf:quals-exploit

RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" apt-get install -y python2.7 build-essential wget python3

RUN wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
RUN python2.7 get-pip.py

RUN apt-get install -y python3
RUN pip install pathlib2

RUN pip install pwntools

COPY solve.py /root/solve.py

WORKDIR /root
CMD ["python2.7", "/root/solve.py"]
