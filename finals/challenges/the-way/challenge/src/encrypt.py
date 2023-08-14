#!/usr/bin/env python3

import arc4
import itertools
import random
import struct
import sys
from pathlib import Path
from Crypto.Protocol.KDF import PBKDF2

base_name = sys.argv[1]
flag = sys.argv[2]
size = int(sys.argv[3])

INT64_MAX = (1 << 64) - 1
INT32_MAX = (1 << 32) - 1
MAX_DIST = INT32_MAX
#MAX_DIST = 10

flag_hash = PBKDF2(flag, b'the-way-flag', count=10000)

template_c = """
#include <stdint.h>
#include "flag.h"
unsigned char flag_encrypted[FLAG_LEN] = {
    %s
};
uint64_t w[8*PROBLEM_SIZE*PROBLEM_SIZE] = {
    %s
};
"""

template_h = """
#define PROBLEM_SIZE %d
#define FLAG_LEN %d
extern unsigned char flag_encrypted[FLAG_LEN];
extern uint64_t w[8*PROBLEM_SIZE*PROBLEM_SIZE];
"""


def print_matrix(matrix):
    for row in matrix:
        print(', '.join(f'{x:20d}' for x in row))


def debug(distance_matrix, path_matrix):
    print_matrix(distance_matrix)
    print()
    print_matrix(path_matrix)
    print()


def generate_distance_matrix(size):
    distance_matrix = []
    for y in range(size):
        distance_matrix.append([])
        for x in range(size):
            if x == y:
                val = 0
            else:
                val = random.randint(0, MAX_DIST)
                if val % 5 == 0:
                    val = INT64_MAX
            distance_matrix[-1].append(val)

    return distance_matrix


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


distance_matrix = generate_distance_matrix(size)
distance_matrix_flat = [
    item for sublist in distance_matrix for item in sublist]
path_matrix = calculate_shortest_path_matrix(distance_matrix)


#debug(distance_matrix, path_matrix)

key = b"".join(b"".join(struct.pack("<Q", x)
               for x in row) for row in path_matrix)
# print(key.hex())
rc4 = arc4.ARC4(key)
ciphertext = rc4.encrypt(flag.encode() + b'\0')

code = template_c % (
    ", ".join(f"{x:#04x}" for x in ciphertext),
    ", ".join(f"{x:#010x}" for x in distance_matrix_flat),
)
header = template_h % (size, len(ciphertext))


with open(f"{base_name}.c", "w") as fout:
    fout.write(code)

with open(f"{base_name}.h", "w") as fout:
    fout.write(header)

src_dir = Path(__file__).parent.parent
with open(src_dir / 'src' / 'server.tpl.py', 'r') as fin:
    server_template = fin.read()
server_code = server_template.replace('FLAG_HASH_PLACEHOLDER', flag_hash.hex())
output_path = src_dir / 'build' / 'server.py'
with open(output_path, 'w') as fout:
    fout.write(server_code)
output_path.chmod(0o0755)
