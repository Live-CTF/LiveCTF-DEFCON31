FROM livectf/livectf:quals-exploit

COPY solve-template.py /solve.py
RUN pip install --no-cache-dir parse

WORKDIR /
CMD ["python3", "solve.py"]
