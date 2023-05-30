#!/usr/bin/env python3
from pwn import *
import sys
#context.log_level = "debug"

sys.setrecursionlimit(100000)

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

from ctypes import *
#libc = CDLL("./libc.so.6")
libc = CDLL("/lib/x86_64-linux-gnu/libc.so.6")

libc.srand(libc.time(0))
io = remote(HOST, int(PORT))
#io = process("./challenge")

def rand_range(min, max):
    return (libc.rand() % (max - min + 1) + min)

def generate_maze(maze, y, x, a4):
    v18 = [0]*8

    maze[30 * y + x] = ord('.');
    v18[0] = 1;
    v18[1] = 0;
    v18[2] = -1
    v18[3] = 0;
    v18[4] = 0;
    v18[5] = 1;
    v18[6] = 0;
    v18[7] = -1

    for i in range(3, 0, -1):
        v15 = rand_range(0, i);
        v16 = v18[2 * i];
        v17 = v18[2 * i + 1];
        v18[2 * i] = v18[2 * v15];
        v18[2 * i + 1] = v18[2 * v15 + 1];
        v18[2 * v15] = v16;
        v18[2 * v15 + 1] = v17;

    for j in range(4):
        v13 = 2 * v18[2 * j] + y;
        v14 = 2 * v18[2 * j + 1] + x;
        if ( v13 > 0 and v13 <= 0x1C and v14 > 0 and v14 <= 0x1C and maze[0x1E * v13 + v14] == 0x23 ):
            maze[0x1E * v18[2 * j] + 0x1E * y + v18[2 * j + 1] + x] = ord('.')
            generate_maze(maze, v13, v14, 0);

    if a4:
        if rand_range(0, 1):
            while True:
                v11 = rand_range(1, 0x1C);
                if maze[v11 + 0x32A] == ord('.'):
                    break
            maze[v11 + 0x348] = 0x2A;
        else:
            while True:
                v12 = rand_range(1, 0x1C);
                if maze[0x1E * v12 + 0x1B] == ord('.'):
                    break
            maze[0x1E * v12 + 0x1C] = 0x2A;

        for k in range(0x1e):
            maze[k + 0x366] = 0x20;
        for m in range(0x1e):
            maze[0x1E * m + 0x1D] = 0x20;

maze = [ord('#')]*(30*30)
generate_maze(maze, 1, 1, 1)

maze2 = []
for y in range(29):
    maze2.append(maze[y*30:y*30+29])

maze = maze2
maze[1][1] = ord('@')

def get_starting_finishing_points():
    for i in range(29):
        if maze[28][i] == ord('*'):
            end = [28, i]
        if maze[0][i] == ord('*'):
            end = [0, i]
        if maze[i][0] == ord('*'):
            end = [i, 0]
        if maze[i][28] == ord('*'):
            end = [i, 28]
    maze[end[0]][end[1]] = ord('.')
    return [1, 1], end

def escape():
    current_cell = rat_path[len(rat_path) - 1]
    if current_cell == finish:
        return

    if maze[current_cell[0] + 1][current_cell[1]] == ord('.'):
        maze[current_cell[0] + 1][current_cell[1]] = ord('@')
        rat_path.append([current_cell[0] + 1, current_cell[1]])
        escape()

    if maze[current_cell[0]][current_cell[1] + 1] == ord('.'):
        maze[current_cell[0]][current_cell[1] + 1] = ord('@')
        rat_path.append([current_cell[0], current_cell[1] + 1])
        escape()

    if maze[current_cell[0] - 1][current_cell[1]] == ord('.'):
        maze[current_cell[0] - 1][current_cell[1]] = ord('@')
        rat_path.append([current_cell[0] - 1, current_cell[1]])
        escape()

    if maze[current_cell[0]][current_cell[1] - 1] == ord('.'):
        maze[current_cell[0]][current_cell[1] - 1] = ord('@')
        rat_path.append([current_cell[0], current_cell[1] - 1])
        escape()

    # If we get here, this means that we made a wrong decision, so we need to
    # backtrack
    current_cell = rat_path[len(rat_path) - 1]
    if current_cell != finish:
        cell_to_remove = rat_path[len(rat_path) - 1]
        rat_path.remove(cell_to_remove)
        maze[cell_to_remove[0]][cell_to_remove[1]] = ord('.')

start, finish = get_starting_finishing_points()
rat_path = [start]
escape()



io.sendlineafter(b"torment: ", b"a")
libc.rand()
io.recvuntil(b"maze.\n")
maze = []
for _ in range(29):
    maze.append(io.recvline().decode().strip())

#for m in maze:
#    print(m)

prev = rat_path[0]
for p in rat_path[1:-1]:
    libc.rand()
    if p[1] > prev[1]:
        io.sendlineafter(b"torment: ", b"e")
        back = "w"
        forth = "e"
    if p[1] < prev[1]:
        io.sendlineafter(b"torment: ", b"w")
        back = "e"
        forth = "w"
    if p[0] > prev[0]:
        io.sendlineafter(b"torment: ", b"s")
        back = "n"
        forth = "s"
    if p[0] < prev[0]:
        io.sendlineafter(b"torment: ", b"n")
        back = "s"
        forth = "n"
    prev = p

p = rat_path[-1]
if p[1] > prev[1]:
    move = "e"
if p[1] < prev[1]:
    move = "w"
if p[0] > prev[0]:
    move = "s"
if p[0] < prev[0]:
    move = "n"

while True:
    r = libc.rand() % 1213
    if r == 1212:
        io.sendlineafter(b"torment: ", move.encode())
        break
    else:
        io.sendlineafter(b"torment: ", back.encode())
        libc.rand()
        io.sendlineafter(b"torment: ", forth.encode())

io.sendline(b'./submitter')
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info(flag)



