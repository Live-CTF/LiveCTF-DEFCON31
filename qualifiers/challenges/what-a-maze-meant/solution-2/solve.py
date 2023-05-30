from ctypes import c_int, c_uint
from datetime import datetime
import copy
import argparse
from pwn import *
import sys

# context.log_level = 'debug'

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000",
                    help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

# https://gist.github.com/integeruser/4cca768836c68751904fe215c94e914c
# http://www.mscs.dal.ca/~selinger/random/
def srand(seed):
    state = {}
    state["r"] = [0 for _ in range(34)]
    state["r"][0] = c_int(seed).value
    for i in range(1, 31):
        state["r"][i] = (16807 * state["r"][i - 1]) % 2147483647
    for i in range(31, 34):
        state["r"][i] = state["r"][i - 31]
    state["k"] = 0
    for _ in range(34, 344):
        rand(state)
    return state


def rand(state):
    state["r"][state["k"]] = state["r"][(state["k"] - 31) %
                               34] + state["r"][(state["k"] - 3) % 34]
    r = c_uint(state["r"][state["k"]]).value >> 1
    state["k"] = (state["k"] + 1) % 34
    return r, state


def calc_rng(message):
    """
    "As you step into the room, you find yourself standing in a %s space."
    "The walls are adorned with %s"
    "and a two large %s dominate the center of the room."
    "You see %d flowers in a vase,"
    "and through a window you stop to count %d stars."
    "The room appears well designed in the %s style."
    """
    part1, message = message.split(b" standing in a ")[1].split(b" space")
    part2, message = message.split(b" adorned with ")[1].split(b" and a")
    part3, message = message.split(b" two large ")[1].split(b" dominate")
    part4, message = message.split(b" You see ")[1].split(b" flowers in")
    part5, message = message.split(b" to count ")[1].split(b" stars.")
    part6, message = message.split(b" in the ")[1].split(b" style.")
    # print(part1)
    # print(part2)
    # print(part3)
    # print(part4)
    # print(part5)
    # print(part6)

    part1_opts = [
        b"cozy",
        b"medium-sized",
        b"spacious",
        b"massive",
    ]
    part2_3_opts = [
        b"bookshelves",
        b"fireplaces",
        b"suits of armor",
        b"tables",
        b"chests",
        b"beds",
        b"paintings",
        b"statues",
        b"tapestries",
        b"candelabras",
        b"chairs",
        b"fountains",
        b"mirrors",
        b"rugs",
        b"curtains",
        b"chess sets",
    ]
    part6_opts = [
        b"Art Deco",
        b"Baroque",
        b"Classical",
        b"Colonial",
        b"Contemporary",
        b"Country",
        b"Gothic",
        b"Industrial",
        b"Mediterranean",
        b"Minimalist",
        b"Neoclassical",
        b"Renaissance",
        b"Rococo",
        b"Romantic",
        b"Rustic",
        b"Victorian",
    ]
    part1_n = part1_opts.index(part1)
    part2_n = part2_3_opts.index(part2)
    part3_n = part2_3_opts.index(part3)
    part4_n = int(part4)
    part5_n = int(part5)
    part6_n = part6_opts.index(part6)
    # print(part1_n)
    # print(part2_n)
    # print(part3_n)
    # print(part4_n)
    # print(part5_n)
    # print(part6_n)

    """
    printf(format: "As you step into the room, you f…",
        var_138[rand.d & 3],
        var_118[(rand s>> 2).d & 0xf],
        var_118[(rand s>> 6).d & 0xf],
        (rand s>> 0xe).d & 0x1f,
        (rand s>> 0xe).d,
        var_98[(rand s>> 0xa).d & 0xf]
    )
    """

    rng_seed = (part1_n) | (part2_n << 2) | (part3_n << 6) | (part5_n << 0xe) | (part6_n << 0xa)
    # print(f"{rng_seed:08x}")
    return rng_seed


# test = calc_rng(b'As you step into the room, you find yourself standing in a medium-sized space. The walls are adorned with curtains and a two large fountains dominate the center of the room. You see 18 flowers in a vase, and through a window you stop to count 3250 stars. The room appears well designed in the Renaissance style.')
# print(f"test: {test:08x}")
# ==> 032caef9
# rand@libc.so.6(0x7ffdac201ea0, 0x7ffdac201fc0, 0, 0x7f935aa99a37) = 0x32caef9
# sys.exit(0)

start_now = int(datetime.now().timestamp())
r = remote(HOST, int(PORT))

r.recvuntil(b"Welcome to the maze!")

rng = []

for i in range(10):
    r.sendline("s")
    r.recvuntil(b"You are in room")
    r.recvuntil(b"\n")
    desc = r.recvuntil(b"Which would you like to do?").split(b"\n")[0]
    rng.append(calc_rng(desc))


def try_match(seed, rng):
    print(f"Trying with seed == {seed}")
    max_tries = 10000
    state = srand(seed)
    j = 0
    for i in range(max_tries):
        r, state = rand(state)
        if r == rng[j]:
            print(f"match {j}...")
            j += 1
            if j == len(rng):
                print("it's a match")
                return True, state
        else:
            if j > 0:
                print("false positive match?")
            j = 0
    print("not a match")
    return False, None

for x in rng:
    print(f"{x:08x}")


offsets = [
    -4,
    -3,
    -2,
    -1,
    0,
    1,
    2,
    3,
    4,
]

guesses = []

for tz_offhours in range(-24, 24):
    tz_off = tz_offhours * 3600
    start = start_now + tz_off
    for offset in offsets:
        guesses.append(start + offset)

seed = None
state = 0
for guess in guesses:
    success, state = try_match(guess, rng)
    if success:
        seed = guess
        break

if seed is None:
    print("Seed match failed :(")
    sys.exit(1)

print(f"Got rand seed: {seed} and {state}")

# confirm it

for i in range(10):
    r.sendline("s")
    r.recvuntil(b"You are in room")
    r.recvuntil(b"\n")
    desc = r.recvuntil(b"Which would you like to do?").split(b"\n")[0]
    real = calc_rng(desc)
    expect, state = rand(state)
    assert real == expect

print("Seed confirmed")

# ok now solve the maze

r.sendline("a")


"""
You cast arcane eye and send your summoned magical eye above the maze.
#############################
#@..#...#.......#.....#.....#
###.#.#.###.###.#.###.#.#.#.#
#.#.#.#...#...#...#.#.#.#.#.#
#.#.#.###.#.#.#####.#.#.#.#.#
#.#.#.#...#.#...#.....#.#.#.#
#.#.#.#.#####.#.#.#######.###
#.#.#.#.....#.#.#.......#...#
#.#.#.#####.###.#######.###.#
#.#.#...#.#.....#.....#.....#
#.#.###.#.#######.#.#######.#
#.#.....#.....#...#.....#...#
#.#######.#.###.#######.#.###
#.........#.#...#.....#.#.#.#
#.###########.###.#####.#.#.#
#...#.......#.#...#.....#.#.#
###.#.#####.#.#.#.#.#####.#.#
#...#.....#.#...#.#.....#.#.#
#.###.#####.#####.#####.#.#.#
#.....#...#.....#...#.#...#.#
#.#####.#.#####.###.#.#####.#
#.#...#.#.........#...#...#.#
#.#.#.#.#########.###.#.#.#.#
#.#.#.#...#...#.....#.#.#...#
#.#.#.###.#.###.#####.#.###.#
#...#.#.#.#.....#...#...#...#
#####.#.#.#######.#.#####.###
#.......#.........#.........#
###########*#################

You are in room (1, 1)
Which would you like to do?
go (e)ast, or (q) end the torment:
"""

maze = []
r.recvuntil("above the maze.\n")

for y in range(29):
    for x in range(29):
        ch = r.recv(1)
        if ch == b'#':
            maze.append(1)
        elif ch == b'@':
            maze.append(0)
            pos = (x, y)
        elif ch == b'*':
            maze.append(0)
            end = (x, y)
        elif ch == b'.':
            maze.append(0)
        else:
            assert False, "unknown maze char"
    assert r.recv(1) == b' '
    assert r.recv(1) == b'\n'


def idx(xy):
    return xy[0]+(xy[1]*29)

def xy(idx):
    return (idx % 29, idx // 29)


for y in range(29):
    for x in range(29):
        if (x, y) == pos:
            print('@', end='')
        elif (x, y) == end:
            print('*', end='')
        else:
            print('#' if maze[idx((x, y))] == 1 else '.', end='')
    print()



# now bfs
seen = set()
queue = [pos]
path = {pos: []}

while len(queue) > 0:
    nx, ny = queue.pop(0)
    seen.add((nx, ny))

    if (nx, ny) == end:
        break

    this_path = path[(nx, ny)]

    walk = [
        (nx - 1, ny),
        (nx + 1, ny),
        (nx, ny - 1),
        (nx, ny + 1),
    ]

    for wx, wy in walk:
        if wx >= 0 and wy >= 0 and wx <= 29 and wy <= 29:
            if maze[idx((wx, wy))] == 0 and (wx, wy) not in seen:
                queue.append((wx, wy))
                path[(wx, wy)] = this_path + [(nx, ny)]

print(path[end])

r.recvuntil(b"Which would you like to do?")

_, state = rand(state)

def get_direction(axy, bxy):
    ax, ay = axy
    bx, by = bxy
    if (bx - ax) == 1:
        return "e"
    if (bx - ax) == -1:
        return "w"
    if (by - ay) == 1:
        return "s"
    if (by - ay) == -1:
        return "n"
    assert False


for i, (axy, bxy) in enumerate(zip(path[end][:-1], path[end][1:])):
    print(f"Solving maze... {i} / {len(path[end])}")
    r.sendline(get_direction(axy, bxy))

    r.recvuntil(b"You are in room")
    r.recvuntil(b"\n")
    desc = r.recvuntil(b"Which would you like to do?").split(b"\n")[0]
    # print(desc)
    real = calc_rng(desc)
    expect, state = rand(state)
    assert real == expect


def is_good_rng(r):
    return (r - (((((r * 0xd81cb3d) >> 0x20) & 0xFFFFFFFF) >> 6) - (r >> 0x1f)) * 0x4bd == 0x4bc)


state2 = copy.deepcopy(state)
i = 0
while True:
    rng, state2 = rand(state2)
    if is_good_rng(rng):
        break
    i += 1

print(f"need to burn {i} walks for good rng")

if i > 1000:
    print("This might time out...")

for j in range(i):
    r.sendline("x")

    r.recvuntil(b"You are in room")
    r.recvuntil(b"\n")
    desc = r.recvuntil(b"Which would you like to do?").split(b"\n")[0]
    # print(desc)
    real = calc_rng(desc)
    expect, state = rand(state)
    assert real == expect
    print(f"Burning walks... {j} / {i}")

next, state2 = rand(state)
assert is_good_rng(next)

r.sendline(get_direction(path[end][-1], end))
r.recvuntil(b"You have solved the maze!")

r.sendline("./submitter")

print(r.recvline_contains("Flag: "))
