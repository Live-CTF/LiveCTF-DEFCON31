#!/usr/bin/env python3

from pwn import *
from ctypes import CDLL

libc = CDLL('/lib/x86_64-linux-gnu/libc.so.6')

#exe = ELF("./challenge_patched")
#libc = ELF("./libc.so.6")
#ld = ELF("./ld-linux-x86-64.so.2")

#context.binary = exe

#!/usr/bin/env python3

from pwn import *

def conn():
    #r = process([exe.path])
    HOST = os.environ.get('HOST', 'localhost')
    PORT = 31337
    r = remote(HOST, int(PORT))

    libc.srand(libc.time(0))
    #r = remote("addr", 1337)
    return r

def rand_range(a, b):
    return a + (libc.rand() % ((b - a) + 1))

def generate_maze(maze, x, y, z):
    something = [1, 0, -1, 0, 0, 1, 0, -1]

    maze[x][y] = '.'
    for i in range(3, 0, -1):
        a = rand_range(0, i)
        b = something[i*2]
        c = something[i*2 + 1]

        something[i*2] = something[a*2]
        something[i*2 + 1] = something[a*2 + 1]
        something[a*2] = b
        something[a*2+1] = c

    for i in range(0, 4, 1):
        b = x + something[i*2]*2
        c = y + something[i*2+1]*2

        if ((((0 < b) and (b < 0x1d)) and (0 < c)) and ((c < 0x1d and (maze[b][c] == '#')))):
            maze[x + something[i*2]][y + something[i*2+1]] = '.'
            generate_maze(maze, b, c, 0)

    if z != 0:
        b = rand_range(0, 1)
        if (b == 0):
            b = rand_range(1, 0x1c)
            while maze[b][0x1b] != '.':
                b = rand_range(1, 0x1c)
            maze[b][0x1c] = '*'
        else:
            b = rand_range(1, 0x1c)
            while maze[0x1b][b] != '.':
                b = rand_range(1, 0x1c)
            maze[0x1c][b] = '*'

        for i in range(0, 0x1e, 1):
            maze[0x1d][i] = ' '

        for i in range(0, 0x1e, 1):
            maze[i][0x1d] = ' '

def display_maze(maze):
    for i in maze:
        print(''.join(i))

def solve_maze(maze):
    start = (1,1)

    VALID = "."
    WALL = "#"
    END = "*"

    MAX_X = 28
    MAX_Y = 29

    #assert(len(maze) == MAX_Y)
    #assert(len(maze[0]) == MAX_X+1)

    # find the goal
    goal = (-1,-1)
    for i in range(MAX_Y):
        for j in range(0,MAX_X+1):
            try:
                if maze[i][j] == "*":
                    goal = (i,j)
            except IndexError:
                print(i)
                print(j)
    if goal == (-1, -1):
        print("no goal!")
        return None

    def _bfs(moves):
        loc = moves[-1]

        # check if won, bubble back up the path
        if maze[loc[0]][loc[1]] == END:
            print("won!")
            return moves

        # recursively call with each new, valid coordinate we could move to (n/s/e/w)
        tgts = [
                (loc[0]-1,loc[1]),
                (loc[0]+1,loc[1]),
                (loc[0],loc[1]-1),
                (loc[0],loc[1]+1),
                ]
        for tgt in tgts:
            if tgt not in moves and maze[tgt[0]][tgt[1]] in (VALID, END):
                x = _bfs(moves + [tgt])
                if x is not None:
                    return x
        return None

    path = _bfs([start])

    # print("\n".join([str(x) for x in path]))

    # convert coords to delta moves
    seq = []
    for i in range(0,len(path)-1):
        now = path[i]
        next = path[i+1]

        if now[0] == next[0]:
            if now[1] - next[1] > 0:
                seq += "w"
            else:
                seq += "e"
        else:
            if now[0] - next[0] > 0:
                seq += "n"
            else:
                seq += "s"

    return seq


back = {'w':'e', 'e':'w', 'n':'s', 's':'n'}

def main():
    r = conn()

    outer = []
    for i in range(0x1e):
        inner = []
        for j in range(0x1e):
            inner.append('#')
        outer.append(inner)

    generate_maze(outer, 1, 1, 1)
    outer[1][1] = '@'
    display_maze(outer)


    libc.rand()
    r.recvuntil(': ')

    sol = solve_maze(outer)
    print(sol)
    for g in range(len(sol)-1):
        r.sendline(sol[g])
        libc.rand()
        r.recvuntil(': ')
 
    while (libc.rand() % 0x4bd) != 0x4bc:
        r.sendline(back[sol[-2]])
        r.recvuntil(': ')
        r.sendline(sol[-2])
        libc.rand()

    r.sendline(sol[-1])
    # good luck pwning :)
    r.recvuntil('Congratulations! You have solved the maze!')

    r.sendline(b'./submitter')
    flag = r.recvline_contains(b'LiveCTF{').decode().strip()
    log.info('Flag: %s', flag)


if __name__ == "__main__":
    main()
