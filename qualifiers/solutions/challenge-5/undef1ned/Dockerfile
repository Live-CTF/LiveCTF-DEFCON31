FROM python:3.11.3-slim-buster

RUN apt update -y && apt upgrade -y
RUN apt install -y build-essential nasm
RUN pip install ptrlib

WORKDIR /app
ADD solve.py .
CMD ["python3", "solve.py"]
