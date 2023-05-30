#!/usr/bin/env python3

from pwn import *


HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
io = remote(HOST, int(PORT))

import sys
from parse import parse, search

from ctypes import CDLL

libc = CDLL("libc.so.6")
t = libc.time(0)
# print(t)
# libc.srand(1685199483)
# print(hex(libc.rand()))

NORTH=0
EAST=1
SOUTH=2
WEST=3
chars = ["n", "e", "s", "w"]
rooms = set()
choice = None
previous = None
buf = ""

def calc(cur, direct):
    (y, x) = cur
    if direct == NORTH:
        y -= 1
    if direct == SOUTH:
        y += 1
    if direct == EAST:
        x += 1
    if direct == WEST:
        x -= 1
    return (y, x)

def opposite(direct):
    if direct is None: return None
    return (direct + 2) % 4

def outside(pos):
    (y, x) = pos
    return x <= 0 or y <= 0 or x >= 28 or y >= 28

def check_seed(seed, n_rots, starlist):
    libc.srand(seed)
    for i in range(n_rots):
        libc.rand()
    j = 0
    for x in starlist:
        v = libc.rand()
        stars = v >> 0xE
        if stars != x:
    #        print(f"stars #{j} didn't match {stars} {x}", file=sys.stderr)
            return False
    return True

def will_escape(seed, n_rots, n_maze, n_shuff):
    libc.srand(seed)
    for i in range(n_rots + n_maze + 2 * n_shuff):
        libc.rand()
    orig = libc.rand()
    edx2 = ((orig * 0xd81cb3d) >> 38)
    ecx2 = orig >> 31
    edx3 = (edx2 - ecx2) * 0x4BD
    res = orig - edx3
    if res == 0x4BC:
        return True
    return False

history = []
rands = 0
maze_rands = 0
starlist = []
finished_gen = False
seed = None
exit_dir = None
shuffle_dir1 = None
shuffle_dir2 = None
while True:
    # newchars = sys.stdin.buffer.read1().decode()
    newchars = io._fillbuffer().decode()
    buf += newchars
    if "Welcome" in buf:
        finished_gen = True
    if not finished_gen:
        for c in newchars:
            if c == '|' or c == '/' or c == '-' or c == '\\':
                rands += 1
    if "displacer" in buf:
        print((x, y), file=sys.stderr)
        print(buf, file=sys.stderr)
        break
    if "end the torment" in buf:
        stars = int(search("count {} stars", buf)[0])
        maze_rands += 1
        starlist.append(stars)
        if len(starlist) == 10 and seed is None:
            for x in [t, t-1, t+1, t-2, t+2, t-3, t+3]:
                if check_seed(x, rands, starlist):
                    seed = x
                    print(f'Found seed {seed}', file=sys.stderr)
        res = search("You are in room ({}, {})", buf)
        x = int(res[0])
        y = int(res[1])
        rooms.add((x, y))
        options = []
        if "(n)orth" in buf:
            options.append(NORTH)
        if "(e)ast" in buf:
            options.append(EAST)
        if "(s)outh" in buf:
            options.append(SOUTH)
        if "(w)est" in buf:
            options.append(WEST)
        previous = None
        if history:
            previous = history[-1]
            choice = (history[-1] + 1) % 4
        else:
            choice = options[0]
        # print(f"cur=({x},{y}), visited={rooms}, options={options}", file=sys.stderr)
        while (not choice in options) or ((calc((x, y), choice) in rooms) and (choice is not opposite(previous))):
            # print("reject=", chars[choice], " calc=", calc((x, y), choice), file=sys.stderr)
            choice = (choice + 3)%4
        if choice is opposite(previous):
            # print("backtrack", file=sys.stderr)
            history = history[:-1]
        else:
            history.append(choice)
        if outside(calc((x,y), choice)):
            exit_dir = choice
            shuffle_dir1 = opposite(previous)
            shuffle_dir2 = previous
            print(f"exiting, {x}, {y}, {choice}", file=sys.stderr)
            break
        # print(chars[choice], flush=True)
        io.sendline(chars[choice])
        # print("choice=", chars[choice], file=sys.stderr)
        buf = ""

shuffles = 0
mid_shuf = False
while True:
    if "end the torment" in buf:
        if mid_shuf:
            log.info("shuffle back")
            io.sendline(chars[shuffle_dir2])
            mid_shuf=False
            shuffles += 1
        elif will_escape(seed, rands, maze_rands, shuffles):
            log.info("escape!!")
            io.sendline(chars[exit_dir])
            break
        else:
            log.info("shuffle in")
            io.sendline(chars[shuffle_dir1])
            mid_shuf=True
        buf = ""
    newchars = io._fillbuffer().decode()
    buf += newchars

buf = ""
getting_flag = True
while True:
    newchars = io._fillbuffer().decode()
    buf += newchars
    if "You have solved the maze!" in buf:
        log.info(buf)
        io.sendline('./submitter; echo 780f7887fd; exit')
        getting_flag=True
        buf = ""
    if "780f7887fd" in buf:
        log.info(buf)
        break

