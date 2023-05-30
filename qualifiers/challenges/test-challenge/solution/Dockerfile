FROM python:slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive

RUN pip install pwntools

COPY solve.py /

WORKDIR /
CMD ["python3", "solve.py"]
