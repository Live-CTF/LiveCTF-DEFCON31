#!/usr/bin/env python3

from pwn import *
import re
from ctypes import CDLL
from ctypes.util import find_library
# context.log_level='DEBUG'

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
# libc = CDLL("./libc.so.6")
_libc = find_library("c")
libc = CDLL(_libc)

context(terminal=['tmux', 'splitw', '-hf', '-p', '70'])
io = remote(HOST, int(PORT))
# io = process("../handout/challenge")
#j gdb.attach(io)
libc.srand(libc.time(0))
random_counter = 0

io.recvuntil(b"... \n")
while True:
    c = io.recv(1)
    if c == b'\n':
        break
    io.recv(1)
    libc.rand()
    random_counter += 1

# junk = io.recvuntil(b"torment:")
io.sendlineafter(b"torment:", b'a')

_ = io.recvuntil(b'maze.\n')
maze_str = io.recvuntil(b"You").decode()
maze = []
start = None
end = None
for i,l in enumerate(maze_str.split("\n")[:-2]):
    row = []
    for j,c in enumerate(l):
        if c == "#":
            row.append(1)
        elif c=='.':
            row.append(0)
        elif c == '@':
            start = (i,j)
            row.append(0)
        elif c == '*':
            end = (i,j)
            row.append(0)
    maze.append(row)

m = [[0 for x in l] for l in maze]
m[start[0]][start[1]] = 1
def make_step(k):
  for i in range(len(m)):
    for j in range(len(m[i])):
      if m[i][j] == k:
        if i>0 and m[i-1][j] == 0 and maze[i-1][j] == 0:
          m[i-1][j] = k + 1
        if j>0 and m[i][j-1] == 0 and maze[i][j-1] == 0:
          m[i][j-1] = k + 1
        if i<len(m)-1 and m[i+1][j] == 0 and maze[i+1][j] == 0:
          m[i+1][j] = k + 1
        if j<len(m[i])-1 and m[i][j+1] == 0 and maze[i][j+1] == 0:
           m[i][j+1] = k + 1
k = 0
while  m[end[0]][end[1]] == 0:
    k += 1
    make_step(k)

# print(maze_str)
# for l in m:
    # print(l)

i, j = end
k = m[i][j]
the_path = [(i,j)]
while k > 1:
  if i > 0 and m[i - 1][j] == k-1:
    i, j = i-1, j
    the_path.append((i, j))
    k-=1
  elif j > 0 and m[i][j - 1] == k-1:
    i, j = i, j-1
    the_path.append((i, j))
    k-=1
  elif i < len(m) - 1 and m[i + 1][j] == k-1:
    i, j = i+1, j
    the_path.append((i, j))
    k-=1
  elif j < len(m[i]) - 1 and m[i][j + 1] == k-1:
    i, j = i, j+1
    the_path.append((i, j))
    k -= 1
cur_x, cur_y = start
the_path.reverse()
the_path = the_path[1:]
last_move = None
for x,y in the_path[:-1]:
    if x > cur_x:
        move = b's'
    elif x < cur_x:
        move = b'n'
    elif y < cur_y:
        move = b'w'
    elif y > cur_y:
        move = b'e'
    else:
        print("WTF")
    io.sendlineafter(b"torment: ", move)
    mm = io.recvuntil(b"room").decode()
    # for l in mm.split("\n"):
    #     print(l)
    new = io.recvline().decode().rstrip()[2:-1]
    cur_x = int(new.split(",")[0])
    cur_y = int(new.split(" ")[1])
    last_move = move
    r = libc.rand()
    random_counter+=1
    # print((r>>0xe)&0x1f)

def calculate_equivalent(value):
    edx = (value & 0xFFFFFFFF)  # Zero-extend the lower 32 bits of value into edx

    # Sign-extend edx to rdx (64 bits)
    rdx = (edx & 0xFFFFFFFF) if edx & 0x80000000 else (edx & 0xFFFFFFFF) | 0xFFFFFFFF00000000

    # Multiply rdx by 0xd81cb3d
    rdx = rdx * 0xd81cb3d

    # Perform right shift and arithmetic right shift
    rdx >>= 32
    edx = (edx >> 6) if edx >= 0 else (edx >> 6) + (0xFFFFFFFF << 26)

    # Copy value to ecx
    ecx = value

    # Perform arithmetic right shift
    ecx = (ecx >> 31) if ecx >= 0 else (ecx >> 31) + 2

    # Subtract ecx from edx
    edx -= ecx

    # Multiply edx by 0x4bd
    ecx = edx * 0x4bd

    # Subtract ecx from eax
    eax = value - ecx

    # Copy eax to edx
    edx = eax

    # Compare edx with 0x4bc
    result = edx == 0x4bc
    # return edx 

    return result


# r = libc.rand()
r = libc.rand()
# print(random_counter)
# print(hex(r))
# print(hex(calculate_equivalent(r)))
x,y = the_path[-1]
if x > cur_x:
    move = b's'
elif x < cur_x:
    move = b'n'
elif y < cur_y:
    move = b'w'
elif y > cur_y:
    move = b'e'
# io.sendlineafter(b"torment:", move)

if last_move == b's':
    undo = b'n'
elif last_move == b'n':
    undo = b's'
elif last_move == b'e':
    undo = b'w'
elif last_move == b'w':
    undo = b'e'
state = 1
print("trying to win")
while True:
    r = libc.rand()
    if state == 1:
        if calculate_equivalent(r) or r%0x4bd == 0x4bc:
        # if r%0x4bd == 0x4bc:
            print("winning")
            io.sendlineafter(b"torment:", move)
            io.sendlineafter(b"maze!", "./submitter")

            try:
                print(io.recvall(timeout=1))
            except:
                pass
            break
        else:
            io.sendlineafter(b"torment:", undo)
            state = 0
    else:
        io.sendlineafter(b"torment:", last_move)
        state = 1
