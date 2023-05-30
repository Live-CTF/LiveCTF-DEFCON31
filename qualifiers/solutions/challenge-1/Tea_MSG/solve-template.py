#!/usr/bin/env python3

import re
import time
from pwn import *
from ctypes import CDLL

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

libc = CDLL("libc.so.6")

history = []
def extract_history(feedback):
    data = re.search(r"stop to count (\d+) stars\.", feedback.decode().replace("\n", " "))
    # print(feedback, data)
    history.append(int(data.group(1)))

io = remote(HOST, int(PORT))

io.recvuntil(b"Reticulating splines")
start_time = libc.time(0)
print(f"Base time {start_time}")

io.recvuntil(b"Welcome to the maze!")
extract_history(io.recvuntil(b"or (q) end the torment: "))
io.sendline(b"a")
io.recvuntil(b"eye above the maze.")

maze_raw = io.recvuntil(b"You are in room")
maze = maze_raw.decode().split("\n")[1:-2]
io.recvuntil(b"or (q) end the torment: ")

maze = [
    [cell for cell in row]
    for row in maze
]

vis = [
    [None for cell in row]
    for row in maze
]
h = len(maze)
w = len(maze[0])

d4 = [
    (0, -1, "w"),
    (0, 1, "e"),
    (-1, 0, "n"),
    (1, 0, "s")
]

me = None
goal = None
for y, row in enumerate(maze):
    for x, cell in enumerate(row):
        if cell == "@":
            me = (y, x)
        elif cell == "*":
            goal = (y, x)

def dfs(y, x):
    for dy, dx, fwd in d4:
        ny, nx = y + dy, x + dx
        if ny < 0 or nx < 0 or ny >= h or nx >= w:
            continue

        # print(ny, nx)
        if vis[ny][nx] is None and maze[ny][nx] != "#":
            vis[ny][nx] = (y, x, fwd)
            dfs(ny, nx)

dfs(*me)
cur = goal
backtrack = []
while cur != me:
    y, x, fwd = vis[cur[0]][cur[1]]
    backtrack.append(fwd)
    cur = (y, x)

path = "".join(backtrack[::-1]).lower()
print(path)

stall = ({
    "w": "ew",
    "e": "we",
    "n": "sn",
    "s": "ns"
})[path[-2]]
print(f"Stalling move is {stall}")

final = path[-1]
print(f"Final move is {final}")

io.sendline(path[:-1].encode())
for _ in range(len(path) - 1):
    extract_history(io.recvuntil(b"or (q) end the torment: "))
print(history)

for offset in range(-5, 5):
    libc.srand(start_time + offset)
    for _ in range(590):
        libc.rand()
    samples = [
        (libc.rand() >> 0xe) & 0xffffffff
        for _ in history
    ]
    if samples == history:
        break
print(f"Found offset {offset}")

while libc.rand() % 0x4bd != 0x4bc:
    print(".", flush=True, end="")
    io.sendline(stall.encode())
    extract_history(io.recvuntil(b"or (q) end the torment: "))
    extract_history(io.recvuntil(b"or (q) end the torment: "))
    assert history[-1] == ((libc.rand() >> 0xe) & 0xffffffff)
io.sendline(final.encode())

io.sendline("./submitter")
io.recvuntil(b"Flag: ")
print(io.recvline())
