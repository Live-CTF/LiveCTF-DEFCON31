#!/usr/bin/env python3
import os
import pwn

import maze_solver
import decode_description

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

r = pwn.remote(HOST, int(PORT))
#r = pwn.process("../handout/challenge")

print("Waiting for maze generation...")

r.recvuntil(b"Welcome to the maze!")
r.recvlines(2)

# Get the initial room state
description = r.recvline().decode("ascii").rstrip()
print(f"Description: {description}")

r.recvuntil(":")

# Find the seed
rand_result = decode_description.decode_description(description)
print(f"Determined rand output: {hex(rand_result)}")
brute_forcer = pwn.process(["./brute_force_seed", hex(rand_result)])
brute_force_output = brute_forcer.recvall().decode("ascii")

print(brute_force_output)

extra_steps = int(brute_force_output.splitlines()[2].split(" ")[3])
print(f"Extra steps: {extra_steps}")


# Get the maze layout
r.sendline(b"a")
r.recvlines(2)
maze_text = r.recvuntil(b"You").decode("ascii")
maze_lines = [line.rstrip() for line in maze_text.split("\n")][:-2]
mazerunner = maze_solver.MazeRunner(None, maze_lines)
path = mazerunner.find_path()
print(path)

r.sendline(path[:-1])

for _ in range(len(path)):
    r.recvuntil(":")

extra_steps = 1 + extra_steps - len(path)

print(f"Need to fill for {extra_steps=}")

# Now do the extra steps
assert(extra_steps % 2 == 1)

penultimate_step = path[-2]
if penultimate_step == "e":
    filler_steps = "we"
elif penultimate_step == "w":
    filler_steps = "ew"
elif penultimate_step == "n":
    filler_steps = "sn"
else:
    filler_steps = "ns"

print(f"Filling with {filler_steps}")

filler = filler_steps * int(extra_steps/2)

r.sendline(filler)

r.sendline(path[-1])

msg = r.recvuntil(b"!")

msg = r.recvuntil(b"!")
print(msg)

msg = r.recvuntil(b"!")
print(msg)

r.sendline("id")
r.sendline(b'./submitter')
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
pwn.log.info('Flag: %s', flag)