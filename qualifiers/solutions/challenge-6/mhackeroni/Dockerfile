
FROM livectf/livectf:quals-exploit
RUN echo 'IyEvYmluL3NoCgpweXRob24zIHNlcnZlci5weQo=' | base64 -d > /challenge
COPY a.py /solve.py
WORKDIR /
RUN python3 -m pip install --upgrade git+https://github.com/JinBlack/libdebug
CMD ["python3", "/solve.py"]