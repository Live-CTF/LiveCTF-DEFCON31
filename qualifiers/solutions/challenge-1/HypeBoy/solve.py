from pwn import *
import sys
import ctypes
from collections import deque

# if len(sys.argv) >= 2:
# p = process('../chall-1/handout/challenge')
# else:
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = remote(HOST, int(PORT))


libc = ctypes.CDLL('/lib/x86_64-linux-gnu/libc.so.6')
libc.srand(libc.time(0))
p.sendlineafter('the torment: ', 'a')

for i in range(591):
  libc.rand()

d = p.recvuntil('the torment: ').decode()
d = (d[d.find('maze.')+6:d.find('You are')])
d = d.split('\n')
maze = d[:-2]
maze = list(map(lambda x: list(x), maze))

# print(maze)
moves = [(0, 1), (0, -1), (1, 0), (-1, 0)] 

# Initializes the starting and ending points
start, end = None, None
for i in range(len(maze)):
    for j in range(len(maze[0])):
        if maze[i][j] == '@':
            start = (i, j)
        if maze[i][j] == '*':
            end = (i, j)

# Implements BFS
visited = set()
queue = deque([(start, [])])
moves = {
    (0, -1): 'w',  # west
    (0, 1): 'e',   # east
    (-1, 0): 'n',  # north
    (1, 0): 's'    # south
}

# BFS initialization goes here...

while queue:
    node, path = queue.popleft()
    if node not in visited:
        visited.add(node)
        if node == end:
            # print(''.join(path))  # Print the path as a series of 'w', 'e', 'n', 's'
            break
        for move, direction in moves.items():
            next_node = (node[0] + move[0], node[1] + move[1])
            if maze[next_node[0]][next_node[1]] not in ['#', '@'] and next_node not in visited:
                new_path = list(path)
                new_path.append(direction)  # Record the direction of the move
                queue.append((next_node, new_path))
# print(path)

cnt = 0

doPath = path[:-1]
# print(doPath)
last2 = path[-2]

if last2 == 'e':
  last1 = 'w'
elif last2 == 'w':
  last1 = 'e'
elif last2 == 'n':
  last1 = 's'
else:
  last1 = 'n'

for i in doPath:
  p.sendline(i)
  p.recvuntil('the torment: ')
  libc.rand()

c = []
for i in range(0x1000):
  c.append(libc.rand() % 1213)

for j in range(len(c)):
   if c[j] == 1212:
      cnt = j
# print((last1, last2))
# print(cnt)
# pause()
r = (last1 + last2) * (cnt // 2) + (last1) * (cnt % 2)
p.sendline(r)
# for i in range(cnt):
#   print(i)
#   if i % 2 == 0:
#     p.sendline(last1)
#   else:
#     p.sendline(last2)
#   p.recvuntil('the torment: ')

# print(path[-1])
# context.log_level='debug'

p.sendline(path[-1])
# while True:
  
#   if libc.rand() % 1213== 1212:
#     break
#   if cnt % 2 == 0:
#     p.sendline('s')
#   else:
#     p.sendline('n')
#   cnt += 1
# p.interactive()

# p.interactive()

p.sendlineafter('solved the maze!\n',b'./submitter', timeout=2)
flag = p.recvline_contains(b'LiveCTF{').decode().strip()

log.info('Flag: %s', flag)
