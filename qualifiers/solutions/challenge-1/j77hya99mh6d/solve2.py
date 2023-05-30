#!/usr/bin/env python3

from pwn import *
import typing as t
from parse import parse
from ctypes import CDLL
from time import time

SIZES = [None] * 4
SIZES[0] = "cozy"
SIZES[1] = "medium-sized"
SIZES[2] = "spacious"
SIZES[3] = "massive"

ITEMS = [None] * 16
ITEMS[0] = "bookshelves"
ITEMS[1] = "fireplaces"
ITEMS[2] = "suits of armor"
ITEMS[3] = "tables"
ITEMS[4] = "chests"
ITEMS[5] = "beds"
ITEMS[6] = "paintings"
ITEMS[7] = "statues"
ITEMS[8] = "tapestries"
ITEMS[9] = "candelabras"
ITEMS[10] = "chairs"
ITEMS[11] = "fountains"
ITEMS[12] = "mirrors"
ITEMS[13] = "rugs"
ITEMS[14] = "curtains"
ITEMS[15] = "chess sets"

STYLES = [None] * 16
STYLES[0] = "Art Deco"
STYLES[1] = "Baroque"
STYLES[2] = "Classical"
STYLES[3] = "Colonial"
STYLES[4] = "Contemporary"
STYLES[5] = "Country"
STYLES[6] = "Gothic"
STYLES[7] = "Industrial"
STYLES[8] = "Mediterranean"
STYLES[9] = "Minimalist"
STYLES[10] = "Neoclassical"
STYLES[11] = "Renaissance"
STYLES[12] = "Rococo"
STYLES[13] = "Romantic"
STYLES[14] = "Rustic"
STYLES[15] = "Victorian"

def get_rs_from_description(desc):
    """
    r1 = r & 3
    r2 = (r >> 2) & 0xf
    r3 = (r >> 6) & 0xf
    r4 = (r >> 0xe) & 0x1f
    r5 = (r >> 0xe) & 0xffffffff
    r6 = (r >> 10) & 0xf
    """
    res = parse('As you step into the room, you find yourself standing in a {size} space. The walls are adorned with {item1} and a two large {item2} dominate the center of the room. You see {flowers:d} flowers in a vase, and through a window you stop to count {stars:d} stars. The room appears well designed in the {style} style.', desc)
    r1 = SIZES.index(res['size'])
    r2 = ITEMS.index(res['item1'])
    r3 = ITEMS.index(res['item2'])
    r4 = res['flowers']
    r5 = res['stars']
    r6 = STYLES.index(res['style'])
    return [r1, r2, r3, r4, r5, r6]

def desc_matches(r, desc):
    # check if the given rand value r matches the desc
    r1 = r & 3
    r2 = (r >> 2) & 0xf
    r3 = (r >> 6) & 0xf
    r4 = (r >> 0xe) & 0x1f
    r5 = (r >> 0xe) & 0xffffffff
    r6 = (r >> 10) & 0xf
    rs = [r1, r2, r3, r4, r5, r6]
    checks = get_rs_from_description(desc)
    # print(rs)
    # print(checks)
    # print()
    return all(r == c for r, c in zip(rs, checks))

def get_rand_seed(base, desc_outputs):
    # bruteforce around the given base using the desc_outputs
    # to find the original seed
    # has to bruteforce the maze generation rand count too

    for offset in range(0, -5, -1):
        for gen_rand_count in range(560, 620):
            libc.srand(base + offset)
            [libc.rand() for _ in range(gen_rand_count)]
            r_outputs = [libc.rand() for _ in range(len(desc_outputs))] 
            if all(desc_matches(r, desc) for r, desc in zip(r_outputs, desc_outputs)):
                # found good rand seed and rand count!
                return base + offset, gen_rand_count

def get_descs_from_conn(conn, n):
    conn.recvuntil(b'As you step into the room')
    conn.unrecv(b'As you step into the room')
    desc = conn.recvline().decode().strip()
    descs = [desc]
    for i in range(n-1):
        # set arcane
        conn.sendlineafter(b'torment: ', b'a')

        # find valid move
        conn.recvuntil(b'go ')
        valid_direction = conn.recv(2).decode()[1]
        conn.sendlineafter(b'torment: ', valid_direction.encode())

        conn.recvuntil(b'As you step into the room')
        conn.unrecv(b'As you step into the room')
        desc = conn.recvline().decode().strip()
        descs.append(desc)
    return descs

def count_arcanes_for_good(seed, maze_count, N_descs, step_count):
    # maze_count is number of rand calls for maze generation
    # N_descs is how many times we've received the arcane descriptions (each one rand)
    # step_count is how many steps to get to the end of the maze
    libc.srand(seed)
    [libc.rand() for _ in range(maze_count + N_descs + step_count)]
    how_many = 0
    while True:
        r = libc.rand()
        if r % 0x4bd == 0x4bc and how_many % 2 == 0:
            break
        how_many += 1
    return how_many

OPPOSITE = {'w':'e','e':'w','s':'n','n':'s'}
def loop_arcanes(conn, N):
    # loop back and forth N times
    next_move = None
    for i in range(N):
        conn.sendline(b'a')

        # find valid move
        conn.recvuntil(b'go ')
        valid_direction = conn.recv(2).decode()[1]
        if next_move is None:
            next_move = valid_direction
        else:
            next_move = OPPOSITE[next_move]
        conn.sendlineafter(b'torment: ', next_move.encode())

libc = CDLL('/lib/x86_64-linux-gnu/libc.so.6')
# libc = CDLL('../handout/libc.so.6')

def main():
    base = int(time())
    HOST = os.environ.get('HOST', 'localhost')
    PORT = 31337

    io = remote(HOST, int(PORT))

    # io = process('../handout/challenge')

    # get good state
    N_descs = 50
    descs = get_descs_from_conn(io, N_descs)
    seed, maze_count = get_rand_seed(base, descs)
    print('seed:', seed)
    print('maze_count:', maze_count)

    # solve maze

    io.sendafter(b'end the torment: ', b'a')
    io.recvline_contains(b'You cast arcane eye and send your summoned magical eye above the maze.')

    maze_str = ''
    for i in range(29):
        maze_str += io.recvline().decode().strip() + '\n'

    # List of maze steps eg ['n', 'e', 'n', 'w', 's']
    maze_steps = [c for c in solve_maze(maze_str)]

    for step in maze_steps[:-1]:
        io.sendlineafter(b'nd the torment: ', step.encode())

    N_arcanes = count_arcanes_for_good(seed, maze_count, N_descs, len(maze_steps)-1)
    print('N_arcanes:', N_arcanes)
    # now go back and forth
    loop_arcanes(io, N_arcanes)
    print('arcanes done, now step to win')

    io.sendlineafter(b'nd the torment: ', maze_steps[-1].encode())

    io.recvuntil(b'Congratulations!')
    print(io.recvline().decode())
    io.sendline(b'./submitter')
    flag = io.recvline_contains(b'LiveCTF{').decode().strip()
    print('Flag: %s', flag)

def solve_maze(maze_str: str) -> str:
    maze, start = __parse_maze(maze_str)
    return __crack_maze(maze, start)

def __parse_maze(maze_str: str) -> t.Tuple[t.List[t.List[int]], t.Tuple[int, int]]:
    maze = [[0 for _ in range(29)] for _ in range(29)]
    start = (-1, -1)

    for y, row in enumerate(maze_str.strip().split('\n')):
        for x, c in enumerate(row):
            if c == '#':
                maze[y][x] = 0
            elif c == '.':
                maze[y][x] = 1
            elif c == '@':
                maze[y][x] = 1
                start = (y, x)
            elif c == '*':
                maze[y][x] = 3
            else:
                raise Exception(f'dang: "{c}"')
            

    return maze, start

def __crack_maze(maze: t.List[t.List[int]], start: t.Tuple[int, int]):
    def crack_step(position: t.Tuple[int, int], prev_positions: set):
        for direction in 'nswe':
            if direction == 'n':
                next_pos = (position[0] - 1, position[1])
            elif direction == 's':
                next_pos = (position[0] + 1, position[1])
            elif direction == 'w':
                next_pos = (position[0], position[1] - 1)
            elif direction == 'e':
                next_pos = (position[0], position[1] + 1)
            else:
                raise Exception('dang')
            
            
            next_value = maze[next_pos[0]][next_pos[1]]
            if next_value == 0:
                continue # wall
            elif next_value == 3:
                return direction # finish

            if next_pos not in prev_positions:
                next_prev_positions = prev_positions.copy()
                next_prev_positions.add(next_pos)
                next_directions = crack_step(next_pos, next_prev_positions)
                if next_directions is not None:
                    return direction + next_directions

    return crack_step(start, set([start]))

if __name__ == "__main__":
    main()
