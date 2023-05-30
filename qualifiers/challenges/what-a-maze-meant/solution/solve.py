import argparse
from time import time
from ctypes import CDLL
from pwn import *
from math import floor
import sys

def check_room(room_random, size, object1, object2, style, flowers, stars):
    sizes = ["cozy", "medium-sized", "spacious", "massive"]
    objects = ["bookshelves", "fireplaces", "suits of armor", "tables", "chests", "beds", "paintings", "statues", "tapestries", "candelabras", "chairs", "fountains", "mirrors", "rugs", "curtains", "chess sets" ]
    styles = ["Art Deco", "Baroque", "Classical", "Colonial", "Contemporary", "Country", "Gothic", "Industrial", "Mediterranean", "Minimalist", "Neoclassical", "Renaissance", "Rococo", "Romantic", "Rustic", "Victorian"]
    size_index = room_random & 0b11
    object_index_1 = (room_random >> 2) & 0b1111
    object_index_2 = (room_random >> 6) & 0b1111
    style_index = (room_random >> 10) & 0b1111
    flower_count = (room_random >> 14) & 0b11111
    star_count = room_random >> 14
    if sizes[size_index] == size and \
            objects[object_index_1] == object1 and \
            objects[object_index_2] == object2 and \
            styles[style_index] == style and \
            flower_count == flowers and \
            star_count == stars:
        return True
    else:
        return False

def next_random(libc, seed, count):
    libc.srand(seed)
    for _ in range(count):
        libc.rand()
    return libc.rand()

#context.log_level = 'debug'

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000",
                    help="Address of challenge")

args = parser.parse_args()

libc = CDLL("libc.so.6")
if ":" in args.address:
    HOST, PORT = args.address.split(':')
    conn = remote(HOST, int(PORT))
else:
    conn = process("./challenge")
now = int(floor(time.time()))
libc.srand(now)

welcome = conn.recvuntil("\n")
generation = conn.recvline() 
spinner = b"|/-\\";
random_count = 0
for char in spinner:
    random_count += generation.count(char)

print(f"I found {random_count} total rand calls")

conn.recvline() # Empty
conn.recvline() # Welcome
conn.recvline() # You are in room
room = conn.recvline() # Room Description
room_words = room.split(b" ")

conn.recvline() #  Which would you like to do?
star_offset = room_words.index(b"stars.")
stars = int(room_words[star_offset - 1])

for seed in range(now - 10, now + 10):
    next = next_random(libc, seed, random_count)
    if stars == next >> 14:
        break
else:
    print("Failed to match seed")
    sys.exit(-1)

print(f"Random seed was: {seed}")

DIMENSIONS=30
x = 1
y = 1
facing = "s"

def move_e():
    conn.sendline(b"e")
    global y
    y += 1

def move_w():
    conn.sendline(b"w")
    global y
    y -= 1

def move_n():
    conn.sendline(b"n")
    global x
    x -= 1

def move_s():
    conn.sendline(b"s")
    global x
    x += 1


while True:
    random_count += 1 # room description
    choices = conn.recvuntil(": ")
    if b"(e)" in choices and y == (DIMENSIONS-3):
        print(f"SOLVED IT, BRUTE WIN ({random_count})")
        if b"(w)" in choices:
            othermove=b"we"
        if b"(n)" in choices:
            othermove=b"ns"
        if b"(s)" in choices:
            othermove=b"sn"
        while (next_random(libc, seed, random_count) % 1213) != 1212:
            random_count += 2
            conn.sendline(othermove)
            conn.recvuntil(": ")
        conn.sendline(b"e")
        break

    if b"(s)" in choices and x == (DIMENSIONS-3):
        print(f"SOLVED IT, BRUTE WIN ({random_count})")
        if b"(w)" in choices:
            othermove=b"we"
        if b"(e)" in choices:
            othermove=b"ew"
        if b"(n)" in choices:
            othermove=b"ns"
        while (next_random(libc, seed, random_count) % 1213) != 1212:
            random_count += 2
            conn.sendline(othermove)
            conn.recvuntil(": ")
        conn.sendline(b"s")
        break

    match facing:
        case "s":
            if b"(w)" in choices:
                facing = "w"
                move_w()
                continue
            if b"(s)" in choices:
                move_s()
                continue
            if b"(e)" in choices:
                facing = "e"
                move_e()
                continue
            else:
                # Only path is back the way we came
                facing = "n"
                move_n()
        case "n":
            if b"(e)" in choices:
                facing = "e"
                move_e()
                continue
            if b"(n)" in choices:
                move_n()
                continue
            if b"(w)" in choices:
                facing = "w"
                move_w()
                continue
            else:
                # Only path is back the way we came
                facing = "s"
                move_s()
        case "e":
            if b"(s)" in choices:
                facing = "s"
                move_s()
                continue
            if b"(e)" in choices:
                move_e()
                continue
            if b"(n)" in choices:
                facing = "n"
                move_n()
                continue
            else:
                # Only path is back the way we came
                facing = "w"
                move_w()
        case "w":
            if b"(n)" in choices:
                facing = "n"
                move_n()
                continue
            if b"(w)" in choices:
                move_w()
                continue
            if b"(s)" in choices:
                facing = "s"
                move_s()
                continue
            else:
                # Only path is back the way we came
                facing = "e"
                conn.sendline(b"e")

conn.recvuntil("Congratulations")
conn.sendline("./submitter;echo \"DONE\"")
print(conn.recvuntil("DONE"))
#conn.interactive()
