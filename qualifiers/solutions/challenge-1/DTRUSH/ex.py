from pwn import *
from ctypes import CDLL
import sys
import time
from math import *
argv = sys.argv
libc = CDLL("libc.so.6")

test = b"As you step into the room, you find yourself standing in a spacious space. The walls are adorned with fireplaces and a two large paintings dominate the center of the room. You see 23 flowers in a vase, and through a window you stop to count 51863 stars. The room appears well designed in the Country style."

part1 = [b"cozy",
b"medium-sized",
b"spacious",
b"massive"]

part2 = [b"bookshelves",
b"fireplaces",
b"suits of armor",
b"tables",
b"chests",
b"beds",
b"paintings",
b"statues",
b"tapestries",
b"candelabras",
b"chairs",
b"fountains",
b"mirrors",
b"rugs",
b"curtains"]

part3 = [b"Art Deco",
b"Baroque",
b"Classical",
b"Colonial",
b"Contemporary",
b"Country",
b"Gothic",
b"Industrial",
b"Mediterranean",
b"Minimalist",
b"Neoclassical",
b"Renaissance",
b"Rococo",
b"Romantic",
b"Rustic",
b"Victorian"]

def get_rnd_value(data):
    rnd1 = data.split(b"standing in a ")[1].split(b' space')[0]
    p1 = part1.index(rnd1)
    rnd2 = data.split(b"adorned with ")[1].split(b' and a two')[0]
    p2 = part2.index(rnd2)
    rnd3 = data.split(b"a two large ")[1].split(b' dominate the')[0]
    p3 = part2.index(rnd3)
    rnd4 = data.split(b"you stop to count ")[1].split(b' stars')[0]
    p4 = int(rnd4.decode())
    rnd5 = data.split(b"designed in the ")[1].split(b' style.')[0]
    p5 = part3.index(rnd5)
    huy = p1 + (p2 << 2) + (p3 << 6) + (p5 << 10) + (p4 << 14)
    return reCalc(590, [huy])

def srand(seed):
    libc.srand(seed)

def rand():
    return libc.rand()

def reCalc(numberOfRandoms, randoms):
    now = int(floor(time.time()))
    for seed in range(now-18000, now+18000):
        srand(seed)
        for i in range(numberOfRandoms):
            rand()
        for i in range(len(randoms)):
            if (rand() != randoms[i]):
                break
            if i == len(randoms)-1:
                cnt = 0
                while (rand() % 1213 != 1212):
                    cnt+=1
                return cnt

def count(p):
    x = p.recvuntil(b'Welcome to the maze!')
    return x.count(b'\r')

def solve_maze(inp: str):
    import queue

    maze = []
    start = 0, 0
    for i, line in enumerate(inp.strip().split('\n')):
        if line != '':
            maze.append(line.strip())
            if '@' in line:
                start = line.find('@'), i
    q = queue.Queue()
    q.put(start)
    w = len(maze[0])
    h = len(maze)
    path = [[None for _ in range(w)] for _ in range(h)]
    path[start[1]][start[0]] = (-100000, -10000)
    visited = [[False for _ in range(w)] for _ in range(h)]
    d = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    finish = (-1, -1)
    while not q.empty():
        ux, uy = q.get()
        for dx, dy in d:
            vx = ux + dx
            vy = uy + dy
            if vx < 0 or vx >= w or vy >= h or vy < 0 or maze[vy][vx] == '#' or visited[vy][vx]:
                continue
            
            visited[vy][vx] = True
            q.put((vx, vy))
            path[vy][vx] = (-dx, -dy)
            if maze[vy][vx] == '*':
                finish = vx, vy
                break

        if finish != (-1, -1):
            break

    traceback = ''
    c = finish
    d = {
        (0, 1): 'n',
        (0, -1): 's',
        (1, 0): 'w',
        (-1, 0): 'e',
    }

    while c != start:
        ux, uy = c
        dx, dy = path[uy][ux]
        traceback += d[(dx, dy)]
        c = ux + dx, uy + dy

    return traceback[::-1]


#p = process('./challenge')
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
p = remote(HOST, int(PORT))
get = count(p)

descr = p.recvuntil(b"end the torment:")
amount = get_rnd_value(descr)+1
p.sendline(b'a')
x = p.recvuntil(b'You are in room').split(b'eye above the maze.\n')[-1].split(b' \n                              \nYou are in room')[0]
x = x.decode()
print(x)
path = solve_maze(x)

op = {'n': 's', 's': 'n', 'w': 'e', 'e': 'w'}

for i in path[:-1]:
    p.sendline(i.encode())
    p.recvuntil(b'You are in room')

amount = amount - len(path) + 1
# my_path = op[path[-1]]
for i in range(amount//2):
    p.sendline(op[path[-2]].encode())
    p.recvuntil(b'You are in room')
    p.sendline(path[-2].encode())
    p.recvuntil(b'You are in room')

p.sendline(path[-1].encode())
p.sendline(b'./submitter')
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
print('Flag:', flag, flush=True)
#log.info('Flag: %s', flag)


