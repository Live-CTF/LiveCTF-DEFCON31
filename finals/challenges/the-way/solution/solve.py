import argparse
import itertools
import arc4

from pwn import *

SIZE_PROBLEM = 0x32
#SIZE_PROBLEM = 5
ADDR_DISTANCE = 0x4060
SIZE_FLAG = 0x24
ADDR_FLAG = 0x4020

INT64_MAX = (1 << 64) - 1

def calculate_shortest_path_matrix(distance_matrix):
    size = len(distance_matrix)
    assert all(len(row) == size for row in distance_matrix)

    path_matrix = [[INT64_MAX for _ in range(size)] for _ in range(size)]

    for i, j in itertools.product(range(size), repeat=2):
        path_matrix[j][i] = distance_matrix[j][i]

    for i in range(size):
        path_matrix[i][i] = 0

    for k, i, j in itertools.product(range(size), repeat=3):
        path_matrix[j][i] = min(
            path_matrix[j][i], path_matrix[k][i] + path_matrix[j][k], INT64_MAX
        )

    return path_matrix

elf = ELF('../../../handouts/the-way/handout/challenge')

distance_bytes = elf.read(ADDR_DISTANCE, 8*SIZE_PROBLEM*SIZE_PROBLEM)
flag_encrypted = elf.read(ADDR_FLAG, SIZE_FLAG)

distance_matrix = []
for y in range(SIZE_PROBLEM):
    distance_matrix.append([])
    for x in range(SIZE_PROBLEM):
        chunk, distance_bytes = distance_bytes[:8], distance_bytes[8:]
        distance_matrix[-1].append(u64(chunk))

path_matrix = calculate_shortest_path_matrix(distance_matrix)

key = b"".join(b"".join(struct.pack("<Q", x) for x in row) for row in path_matrix)
rc4 = arc4.ARC4(key)
flag_decrypted = rc4.decrypt(flag_encrypted)

log.info('Flag: %s', flag_decrypted.decode().strip('\0'))

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")
args = parser.parse_args()
HOST, PORT = args.address.split(':')
r = remote(HOST, int(PORT))

r.sendline(flag_decrypted.decode().strip('\0'))

r.interactive()
