#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

r = remote(HOST, int(PORT))
with open("/link.ld", 'rb') as f:
    content = f.read()
r.sendline(content)
r.recvuntil(b'flag=')
print(r.recvline())
r.close()
exit()
