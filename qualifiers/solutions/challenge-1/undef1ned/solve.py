import os
import ctypes
from ptrlib import *
from time import sleep

#BIN_NAME = 'handout/challenge'
# REMOTE_ADDR = 'localhost'
# REMOTE_LIBC_PATH = 'libc-2.31.so'
# REMOTE_PORT = 3141592
#LOCAL = True

# if LOCAL: stream = process(BIN_NAME)
# else: stream = remote(REMOTE_ADDR, REMOTE_PORT)

#stream = process(BIN_NAME)

HOST = os.getenv('HOST', 'localhost')
PORT = 31337 #os.getenv('PORT', 31337)

#stream = process(["./challenge"])
stream = Socket(HOST, PORT)

arr1 = ["cozy",
      "medium-sized",
      "spacious",
      "massive",]
arr2 = ["bookshelves",
        "fireplaces",
        "suits of armor",
        "tables",
        "chests",
        "beds",
        "paintings",
        "statues",
        "tapestries",
        "candelabras",
        "chairs",
        "fountains",
        "mirrors",
        "rugs",
        "curtains",
        "chess sets",]
arr3 = ["Art Deco",
        "Baroque",
        "Classical",
        "Colonial",
        "Contemporary",
        "Country",
        "Gothic",
        "Industrial",
        "Mediterranean",
        "Minimalist",
        "Neoclassical",
        "Renaissance",
        "Rococo",
        "Romantic",
        "Rustic",
        "Victorian",]

USE_CTYPES = False

if USE_CTYPES:
    #sock = Socket(HOST, PORT)
    libc = ctypes.CDLL("./libc.so.6")
    libc.srand(libc.time(0))
    def rand():
        return libc.rand()
else:
    rrrr = process("./show_rand")
    def rand():
        r = int(rrrr.recvline())
        rrrr.sendline("")
        return r


stream.recvuntil("Welcome")
print("generated.")

def prompt(neko):
    stream.sendlineafter(": ", neko)


v1 = stream.recvregex("you find yourself standing in a (.+) space\.")[0]
v2 = stream.recvregex("adorned with (.+) and a")[0]
v3 = stream.recvregex("two large (.+) dominate")[0]
v4 = int(stream.recvregex("You see (\d+) flowers")[0])
v5 = int(stream.recvregex("stop to count (\d+) stars")[0])
v6 = stream.recvregex("in the (.+) style\.")[0]
v1 = arr1.index(v1.decode())
v2 = arr2.index(v2.decode())
v3 = arr2.index(v3.decode())
v6 = arr3.index(v6.decode())
r = (v1) | (v2 << 2) | (v3 << 6) | (v4 << 14) | (v5 << 14) | (v6 << 10)

while True:
    if rand() == r:
        break

"""
stream.recvuntil("go (")

"""
  

H = 29
W = 29

def get_maze():
    prompt("a")
    stream.recvuntil("maze.\n")

    maze = []
    start, end = None, None
    for i in range(H):
        maze.append(stream.recvline().decode())
    # print(maze)
    for i in range(H):
        for j in range(W):
            if maze[i][j] == "@":start = (i, j)
            if maze[i][j] == "*": end = (i, j)
    
    return maze, start, end

def solve_maze(maze, s, g):
    diff = {
        "n": (-1, 0),
        "w": (0, -1),
        "s": (1, 0),
        "e": (0, 1)
    }
    def transition(state):
        # print(state)
        i, j = state
        for key, (dy, dx) in diff.items():
            ni, nj = i + dy, j + dx
            if 0 <= ni < H and 0 <= nj < W:
                if maze[ni][nj] == "#": continue
                yield ((ni, nj), 1, key)
    sp = ShortestPath(transition)
    hoge, fuga = sp[s][g]
    return fuga.value

maze, start, end = get_maze()

is_valid = False

res = solve_maze(maze, start, end)

for s in res[:-1]:
    rand()
    prompt(s)

dic = {
    "e": ["w","e"],
    "w": ["e","w"],
    "s": ["n","s"],
    "n": ["s","n"],
}

rand()

hogehoge = dic[res[-2]]
# print(hogehoge)
while True:
    prompt(hogehoge[0])
    hogehoge.reverse()
    rand()
    prompt(hogehoge[0])
    hogehoge.reverse()
    next_next_rand = rand()
    # print(next_next_rand)
    if next_next_rand % 1213 == 1212: break

prompt(res[-1])
sleep(1)
stream.sendline("./submitter")
print(stream.recvline())
print(stream.recvline())
print(stream.recvline())
print(stream.recvline())

stream.close()
