#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
with open("/test.ld") as fd:
    script = fd.read()
# script="""SECTIONS
# {
# . = 0x10000;
# .text : { *(.text) }
# . = 0x8000000;
# .data : { *(.data) }
# .bss : { *(.bss) }
# }
# """
log.info("sending script")
log.info(script)
io.sendline(script)
print(io.recvall(timeout=10))
# io.interactive()
