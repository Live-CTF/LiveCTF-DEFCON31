#!/usr/bin/env python3

from pwn import *
import base64
import re
import os

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
p = io

def deobfu(obfu, key):
    arr = [i for i in range(256)]
    j = 0
    for i in range(256):
        v = arr[i]
        j = (j + v + key[i & 0x1f]) % 256
        arr[i] = arr[j]
        arr[j] = v
    v2 = 0
    for i in range(256):
        v2 = (v2 + 1) & 0xff
        v = arr[v2]
        j = (j + v) % 256
        arr[v2] = arr[j]
        arr[j] = v
        obfu[i] = obfu[i] ^ arr[(v + arr[v2]) % 256]

def keygen(elf):
    key_code_marker = b"\x89\xce\x83\xe6\x1f\x44\x00\xc0\x02\x86"
    key_code_offset = elf.index(key_code_marker) + len(key_code_marker)
    key_offset = int.from_bytes(elf[key_code_offset:key_code_offset+2], 'little')

    data = [c for c in elf[0x348:0x348+256]]
    key = [c for c in elf[key_offset:key_offset+32]]
    deobfu(data, key)
    data = bytes(data)

    code = disasm(data)
    assert(r := re.findall("DWORD PTR \[edi\+0x8\], (.*)", code))
    pass_len = int(r[0], 0)
    print("Pass length:", pass_len)

    password = ""
    assert(r := re.findall("BYTE PTR \[eax\], (.*)", code))
    password += chr(int(r[0], 0))
    for i in range(1, pass_len):
        assert(r := re.findall("BYTE PTR \[eax\+" + hex(i) + "\], (.*)", code))
        password += chr(int(r[0], 0))

    return password

p.recvuntil(b"Round 1/")
n_rounds = int(p.recvline())
for i in range(n_rounds):
    print("Round", i+1, "/", n_rounds)
    p.recvuntil(b"Crackme: ")
    elf = base64.b64decode(p.recvline())
    password = keygen(elf)
    print("Password:", password)
    p.recvuntil(b"Password: ")
    p.sendline(password.encode())

p.interactive()
