from pwn import *
import os
from libdebug import Debugger


def solve(bin_name):
	context.binary = bin_name
	r = process(bin_name)

	d = Debugger()
	d.attach(r.pid)

	mmap = 0x2027F9
	d.breakpoint(mmap)

	r.sendline(b"A" * 0x10)
	d.cont()
	d.cont()

	d.step()
	mmapped = d.rax
	d.breakpoint(mmapped, hw=True)

	d.cont()

	sh = d.mem[d.rip : d.rip + 0x100]

	l = sh[4]
	print(hex(l))

	code = disasm(sh).splitlines()[3::2]
	code = code[:l]
	pwd = [int(x.split()[-1], 16) for x in code]
	d.detach()
	r.kill()

	return bytes(pwd)

HOST = os.environ.get("HOST", "localhost")
PORT = 31337
io = connect(HOST, int(PORT))


for i in range(20):
	io.recvuntil(b"Crackme: ")
	binary = b64d(io.recvline().strip())
	with open("/tmp/bin", "wb") as f:
		f.write(binary)
	os.system("chmod +x /tmp/bin")
	pwd = solve("/tmp/bin")
	io.sendlineafter(b"Password: ", pwd)
	print(io.recvline())

print(io.recvall(timeout=1))
