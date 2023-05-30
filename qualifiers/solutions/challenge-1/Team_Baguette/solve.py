#!/usr/bin/env python3

from pwn import *
import subprocess

"""
exe = ELF("../handout/challenge_patched")
libc = ELF("../handout/libc.so.6")
ld = ELF("../handout/ld-linux-x86-64.so.2")

context.binary = exe
"""

def conn():
    """
    if not args.REMOTE:
        r = process([exe.path])
        if args.DBG:
            gdb.attach(r)
    """
    if True:
        HOST = os.environ.get('HOST', 'localhost')
        PORT = 31337
        r = remote(HOST, PORT)
    return r

def solve_maze(maze_str):
    maze = maze_str.decode().split("\n")[:-1]
    maze = [[c for c in line.replace(" ", "")] for line in maze]
    # Find target
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == "*":
                target = (x, y)

    # Use DFS to generate all paths
    maze[1][1] = '0'
    i = 0
    while any("*" in line for line in maze):
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == str(i-1):
                    if y + 1 < len(maze) and maze[y+1][x] in '*.':
                        maze[y+1][x] = str(i)
                    if y - 1 >= 0 and maze[y-1][x] in '*.':
                        maze[y-1][x] = str(i)
                    if x + 1 < len(maze[0]) and maze[y][x+1] in '*.':
                        maze[y][x+1] = str(i)
                    if x - 1 >= 0 and maze[y][x-1] in '*.':
                        maze[y][x-1] = str(i)
        i += 1

    # Go reverse from the exit to generate the path
    x, y = target
    path = ""
    while i > 0:
        if y + 1 < len(maze) and maze[y+1][x] == str(i-1):
            y += 1
            path = "n" + path
        if y - 1 >= 0 and maze[y-1][x] == str(i-1):
            y -= 1
            path = "s" + path
        if x + 1 < len(maze[0]) and maze[y][x+1] == str(i-1):
            x += 1
            path = "w" + path
        if x - 1 >= 0 and maze[y][x-1] == str(i-1):
            x -= 1
            path = "e" + path
        i -= 1
    return path

r = conn()
r.recvuntil(b"and through a window you stop to count ")
# Count stars
stars = int(r.recvuntil(b" stars").split(b" ")[0].decode())
# Get number of moves we should do
n = int(subprocess.check_output("/get_rand " + str(stars), shell=True))

r.recvuntil(b"end the torment:")
r.sendline(b"a")
r.recvuntil(b"You cast arcane eye and send your summoned magical eye above the maze.\n")
maze_str = b""
for i in range(29):
    maze_str += r.recvline()

path = solve_maze(maze_str)

# Got to the end of the maze
for c in path[:-1]:
    r.recvuntil(b"end the torment: ")
    r.sendline(c.encode())

# Waste time
for i in range(n - len(path)):
    r.recvuntil(b"end the torment: ")
    r.sendline(b"x")

r.recvuntil(b"end the torment: ")
r.sendline(path[-1].encode())

r.recvline_contains(b'Congratulations!')
r.sendline(b'./submitter')
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)

