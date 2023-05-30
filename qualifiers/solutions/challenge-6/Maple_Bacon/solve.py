from pwn import *
HOST = os.environ.get('HOST', 'localhost')
PORT = os.environ.get('PORT', '31337')
import base64

import sys
import os
import re

r = remote(HOST, int(PORT))

for i in range(20):
    r.recvuntil('Crackme: ')
    data = base64.b64decode(r.recvline())
    with open("/bin.bin", "wb") as outf:
        outf.write(data)
    os.chmod("/bin.bin", 0o777)
    output = os.popen(f"gdb --batch -x extract.gdb /bin.bin").read()
    matches = re.findall(r"cmpb +\$0x([0-9a-f]+)", output)
    password = bytes(int(s, 16) for s in matches).decode()
    r.recvuntil('Password:')
    r.sendline(password)

flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('%s', flag)
print(flag)
