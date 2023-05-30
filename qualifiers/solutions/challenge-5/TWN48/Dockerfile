FROM livectf/livectf:quals-exploit
WORKDIR /exp
RUN python3 -c '__import__("os").write(1, __import__("requests").get("https://play.livectf.com/api/challenges/5/download").content)' | tar xvzf -
COPY ./ ./
CMD ["python3", "exploit.py", "REMOTE"]
