#!/usr/bin/env python3

from pwn import *
from ctypes import *
from time import sleep
import os
from collections import deque

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = remote(HOST, int(PORT))

libc = CDLL("/lib/x86_64-linux-gnu/libc.so.6")


libc.srand(libc.time(0))

p.recvuntil("like to do?\n")

p.sendlineafter(": ", "a")

p.recvuntil("maze.\n")
maze = []

for _ in range(29):
    maze.append(list(p.recvline().decode()[:-2]))
rows = len(maze)
cols = len(maze[0])

# 방향: 위, 오른쪽, 아래, 왼쪽
directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

# 시작점과 끝점의 위치를 찾습니다.
start, end = (0, 0), (0, 0)
for i in range(rows):
    for j in range(cols):
        if maze[i][j] == '@':
            start = (i, j)
        elif maze[i][j] == '*':
            end = (i, j)

# BFS 알고리즘을 사용하여 미로를 탐색합니다.
def bfs(start):
    queue = deque([start])
    path = {start: None}

    while queue:
        vertex = queue.popleft()

        if vertex == end:
            return path

        for dx, dy in directions:
            next_vertex = (vertex[0] + dx, vertex[1] + dy)
            if (0 <= next_vertex[0] < rows and 0 <= next_vertex[1] < cols and
                maze[next_vertex[0]][next_vertex[1]] in ['.', '*'] and
                next_vertex not in path):
                queue.append(next_vertex)
                path[next_vertex] = vertex

    return None

path = bfs(start)

result = []

# 최단 경로를 출력합니다.
if path is None:
    ...
else:
    cur = end
    while cur != start:
        maze[cur[0]][cur[1]] = '+'
        cur = path[cur]
        result.append((cur[0], cur[1]))
    maze[start[0]][start[1]] = '@'

result.reverse()

direction_mapping = {
        (0, -1): 'w',  # 위
        (1, 0): 's',  # 아래
        (0, 1): 'e',  # 오른쪽
        (-1, 0): 'n'  # 왼쪽
    }
direction_string = ''.join(direction_mapping[(result[i+1][0]-result[i][0], result[i+1][1]-result[i][1])] for i in range(len(result)-1))

# gdb.attach(p, gdbscript="""
# # pie breakpoint 0x1B80
# # pie breakpoint 0x15D1
# b rand
# """)
           
aa = [b"cozy", b"medium-sized", b"spacious", b"massive"]
bb = [b"bookshelves", b"fireplaces", b"suits of armor", b"tables", b"chests", b"beds", b"paintings", b"statues", b"tapestries", b"candelabras", b"chairs", b"fountains", b"mirrors", b"rugs", b"curtains", b"chess sets"]
cc = [b"Art Deco", b"Baroque", b"Classical", b"Colonial", b"Contemporary", b"Country", b"Gothic", b"Industrial", b"Mediterranean", b"Minimalist", b"Neoclassical", b"Renaissance", b"Rococo", b"Romantic", b"Rustic", b"Victorian"]

def get_rand():
    p.sendlineafter(":", "w")
    p.recvuntil("standing in a ")
    a = p.recvuntil(" sp")[:-3]
    p.recvuntil("adorned with ")
    b = p.recvuntil(" and")[:-4]
    p.recvuntil("two large ")
    c = p.recvuntil(" dom")[:-4]
    p.recvuntil("You see ")
    d = p.recvuntil(" flo")[:-4]
    p.recvuntil("to count ")
    e = p.recvuntil(" sta")[:-4]
    p.recvuntil("d in the ")
    f = p.recvuntil(" sty")[:-4]

    val1 = aa.index(a)
    val2 = bb.index(b)
    val3 = bb.index(c)
    val4 = int(d.decode(), 10)
    val5 = int(e.decode(), 10)
    val6 = cc.index(f)

    return (val1&0x3) | ((val2 << 2)&0xfc) | ((val3 << 6)&0xfc0) | ((val6 << 10)&0x3c00) | ((val5 << 14)&0xffffc000)

value = get_rand()
while libc.rand() != value:
    continue
for _ in range(len(direction_string)):
    libc.rand()
for c in direction_string:
    p.sendlineafter(":", c)

while libc.rand()%1213 != 1212:
    p.sendlineafter(":", "t")

res = p.recvuntil(b'#############################', timeout=1)
if res == '':
    dir = 'e'
else:
    dir = 's'

p.sendlineafter(":", dir)
p.recvuntil(b'You have solved the maze!')

p.sendline(b'./submitter')
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
