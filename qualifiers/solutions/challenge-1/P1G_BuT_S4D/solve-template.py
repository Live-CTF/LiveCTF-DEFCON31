import pwn, os
import subprocess
import time
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

t0 = int(time.time())
sock = pwn.remote(HOST, int(PORT))
#sock = pwn.process(['../handout/challenge'])
sock.sendline('a')
sock.recvuntil('maze.\n')
maze = []
for i in range(29):
    maze.append(sock.recvline().decode().strip())
import queue
q = queue.Queue()
#print(maze)
sy,sx = [(i,j) for i in range(29) for j in range(29) if maze[i][j] == '@'][0]
ey,ex = [(i,j) for i in range(29) for j in range(29) if maze[i][j] == '*'][0]
print(sx,sy)
print(ex,ey)
q.put((sx,sy))
path = dict()
path[sx,sy] = ''
while q.qsize():
    x,y = q.get_nowait()
    for dx,dy,c in [[1,0,'e'],[-1,0,'w'],[0,1,'s'],[0,-1,'n']]:
        nx,ny = x+dx,y+dy
        if nx < 0 or nx >= len(maze[0])  or ny < 0 or ny >= len(maze):
            continue
        if maze[ny][nx] == '#':
            continue
        npath = path[x,y] + c
        if (nx,ny) not in path:
            path[nx,ny] = npath
            q.put((nx,ny))
print(path[ex,ey])
descs = []
for c in path[ex,ey][:-1]:
    sock.sendline(c)
    sock.recvuntil('As you')
    s = 'As you' + sock.recvline().decode()
    descs.append(s)
for t in range(t0, t0+100):
    sp = subprocess.check_output(['/a.out',str(t)])
    sp = sp.decode().splitlines()
    s = '\n'.join(sp[::2])
    try:
        i = s.index(''.join(descs[-5:]))
    except:
        continue
    i = s[:i].count('\n')
    ns = [int(x) for x in sp[1::2]]
    for j in range(i, len(ns)):
        if ns[j] % 1213 == 1212:
            break
    for _ in range(j-i-5):
        sock.sendline('x')
    sock.sendline(path[ex,ey][-1])
    sock.recvuntil('maze!')
    sock.sendline('./submitter')
    print(sock.recvrepeat(1))
    #print(sock.recvall())
    break
