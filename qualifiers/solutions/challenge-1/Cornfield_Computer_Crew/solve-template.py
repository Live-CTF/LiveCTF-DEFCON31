#!/usr/bin/python3
from pwn import *
import time
from ctypes import CDLL
from collections import defaultdict

libc_func = CDLL("libc.so.6")
# elf = ELF("./challenge_patched")
# libc = ELF("./libc.so.6")
# ld = ELF("./ld-linux-x86-64.so.2")

# context.binary = elf
# context.terminal = ["tmux", "splitw", "-h"]


def connect():
    HOST = os.environ.get('HOST', 'localhost')
    PORT = 31337
    p = remote(HOST, int(PORT))

    return p

def show_maze(p):
    p.sendlineafter(b"torment: ", b"a")
    p.recvline()
    p.recvline()
    maze = p.recvuntil(b"You are")
    return maze[:-8]
def solve_maze(maze):
    CURR = "@"
    EMPTY = "."
    WALL = "#"

    def graphify(grid):
        m, n = len(grid), len(grid[0])
        print("m, n", m, n)

        assert (m, n) == (29, 29)

        graph = defaultdict(set)
        for r, row in enumerate(grid):
            for c, cell in enumerate(row):
                for dr, dc in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                    if 0 <= r + dr < m and 0 <= c + dc < n:
                        if grid[r][c] != WALL:
                            if grid[r + dr][c + dc] != WALL:
                                graph[(r, c)].add((r + dr, c + dc))
                                graph[(r + dr, c + dc)].add((r, c))

        return graph

    def bfs(graph, node):
        q = [node]
        d = defaultdict(lambda: float("inf"))

        d[node] = 0
        visited = {node: True}
        anc = {node: node}

        while q:
            curr = q.pop()
            # print("curr", curr)
            # print("asdf", curr, graph[curr])
            # if curr == (m - 1, n - 1):
            #   break

            visited[curr] = True
            for nbr in graph[curr]:
                d[nbr] = min(d[nbr], d[curr] + 1)
                if nbr not in visited:
                    anc[nbr] = curr
                    q.append(nbr)

        return anc

    def traceback(anc, start, goal):
        # print("anc", anc)
        curr = goal
        directions = []
        while curr != start:
            new = anc[curr]
            if curr[0] > new[0]:
                directions.append("s")
            elif curr[1] > new[1]:
                directions.append("e")
            elif curr[1] < new[1]:
                directions.append("w")
            elif curr[0] < new[0]:
                directions.append("n")
            else:
                print("WTF")
                break

            curr = new
        return directions[::-1]

    maze = maze.strip()
    maze = maze.split(b"\n")

    grid = list(map(lambda b: b.decode("utf-8").strip(), maze))
    print("\n".join(grid))

    start = (0, 0)
    goal = (0, 0)

    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == CURR:
                start = (r, c)
            if cell == "*":
                goal = (r, c)

    print("start: ", start)
    print("goal: ", goal)

    graph = graphify(grid)

    print(graph[(1, 1)])

    ancs = bfs(graph, start)
    # print(ancs[(1, 2)], ancs[(2, 1)])
    dirs = traceback(ancs, start, goal)

    return len(dirs), dirs


def move(p, direction):
    if direction == 'north' or direction == 'n':
        p.sendline(b"n")
    if direction == 'south' or direction == 's':
        p.sendline(b"s")
    if direction == 'east' or direction == 'e':
        p.sendline(b"e")
    if direction == 'west' or direction == 'w':
        p.sendline(b"w")


def main():
    stime = int(time.time())
    p = connect()
    s = p.recvuntil(b"Welcome to the maze!")
    rands = s.count(b"\r")
    print(rands)
    p.recvuntil(b"You see ")
    flowers = int(p.recvuntil(b" "))
    p.recvuntil(b"to count ")
    star = int(p.recvuntil(b" "))
    print(flowers, star)

    for i in range(stime, stime+1000):
        libc_func.srand(i)
        for j in range(rands):
            libc_func.rand()
        a = libc_func.rand()
        if ((a>>0xe) & 0xffffffff) == star:
            seed = i
            print(i, i-stime)
            break

    libc_func.srand(seed)
    for i in range(rands):
        libc_func.rand()

    maze = show_maze(p)
    print(maze.decode())
    steps, path = solve_maze(maze)
    print(path)

    for i in range(steps):
        libc_func.rand()

    waste = 0
    while libc_func.rand()%1213 != 1212:
        waste += 1 

    for i in path[:-1]:
        move(p, i)
    for i in range(len(path)):
        p.recvuntil(b"like to do?")
    valid = p.recvuntil(b"(q)")
    for i in [b"(w)", b"(e)", b"(s)", b"(n)"]:
        if i not in valid:
            for j in range(waste):
                move(p,i.decode()[1])
            break

    for i in range(waste-1):
        p.recvuntil(b"like to do?")
    move(p, path[-1])

    p.sendline(b'./submitter')
    flag = p.recvline_contains(b'LiveCTF{').decode().strip()
    log.info('Flag: %s', flag)
    



if __name__ == "__main__":
    main()

