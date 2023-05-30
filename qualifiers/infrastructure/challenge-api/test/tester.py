#!/usr/bin/env python3

import hmac
import io
import jwt
import random
import requests
import tarfile
from typing import Dict

BASE_URL = 'http://localhost:8080'
HMAC_KEY = b'secret_key'

def generate_exploit_upload(files: Dict[str, bytes]) -> io.BytesIO:
    tardata = io.BytesIO()
    with tarfile.open(mode='w:gz', fileobj=tardata) as tar_archive:

        for filename, contents in files.items():
            file_info = tarfile.TarInfo(filename)
            file_info.size = len(contents)
            file_data = io.BytesIO(initial_bytes=contents)
            tar_archive.addfile(file_info, file_data)
    
    tardata.seek(0)
    return tardata #.getvalue()

def get_team_token(team_id: int, key: bytes) -> str:
    return jwt.encode({"team_id": str(team_id)}, HMAC_KEY, algorithm="HS256")

encoded_jwt = get_team_token(random.randint(1000, 9999), HMAC_KEY)

challenges = requests.get(BASE_URL + '/challenges').json()
print(f'Challenges: {challenges}')

challenge_1 = requests.get(BASE_URL + '/challenges/1').json()
print(f'Challenge 1: {challenge_1}')

#challenge_1000 = requests.get(BASE_URL + '/challenges/1000')
#print(f'Challenge 1000: {challenge_1000.text}')

exploit_script = """
#/usr/bin/env python3

from pwn import *
import os

io = remote(os.environ['HOST'], 31337)
io.recvline()
io.sendline(b'WIN')
io.recvline()
io.sendline(b'echo $FLAG')
res = io.recvline()
print(res.decode())
io.sendline(b'exit')
"""

dockerfile = """
#FROM debian:buster-slim
FROM ubuntu:22.10

RUN apt-get update && apt-get install -y python3 python3-pip libffi-dev
RUN pip3 install pwntools
COPY solve.py .

CMD ["python3", "solve.py"]
"""

exploit_archive = generate_exploit_upload({
    'Dockerfile': dockerfile.encode(),
    'solve.py': exploit_script.encode()
})
new_exploit1 = requests.post(BASE_URL + '/challenges/1', headers={'X-LiveCTF-Token': encoded_jwt}, files={'exploit': exploit_archive}) #.json()
print(f'Exploit: {new_exploit1.text}')

#new_exploit2 = requests.post(BASE_URL + '/challenges/1', headers={'X-LiveCTF-Token': encoded_jwt})
#print(f'Exploit: {new_exploit2.text}')

#new_exploit3 = requests.post(BASE_URL + '/challenges/1000', headers={'X-LiveCTF-Token': encoded_jwt})
#print(f'Exploit: {new_exploit3.text}')

#new_exploit1 = requests.post(BASE_URL + '/challenges/1', headers={'X-LiveCTF-Token': encoded_jwt}).json()
#print(f'Exploit: {new_exploit1}')
