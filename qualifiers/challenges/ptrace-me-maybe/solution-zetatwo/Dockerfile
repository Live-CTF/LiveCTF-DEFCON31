FROM python:slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get -y install binutils build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN pip install pwntools

COPY solve.py /

WORKDIR /
CMD ["python3", "solve.py"]
