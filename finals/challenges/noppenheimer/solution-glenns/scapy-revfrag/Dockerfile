FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpcap-dev

# Install Scapy using pip
RUN pip install scapy pwntools

RUN pip uninstall pyelftools -y
RUN pip install pyelftools==0.29

RUN apt-get install -y iptables net-tools
RUN apt-get install -y tmux tcpdump iproute2
COPY connect.py .

ENTRYPOINT ["/app/connect.py"]
