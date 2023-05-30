import argparse
import os
import subprocess

from base64 import b64decode

from pwn import *

ALPHABET = b"1234567890abcdef"

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")

args = parser.parse_args()

HOST, PORT = args.address.split(':')


def solve_bin():
    st = os.stat('chal_bin')
    os.chmod('chal_bin', st.st_mode | stat.S_IEXEC)
    max_tries = 2
    for try_num in range(max_tries):
        guess_base = []
        guess_len = 0x20

        while len(guess_base) < guess_len:
            print(b''.join(guess_base) + b'?' * (guess_len - len(guess_base)), end='\r')
            maxnum = 0
            maxchar = ""
            for gc in ALPHABET:
                gc = bytes([gc])
                guess = guess_base + [gc for i in range(0x20 - len(guess_base))]
                a = subprocess.run(["perf", "stat", "-e", "instructions:u", "--", "./chal_bin"], check=True, input=b''.join(guess), capture_output=True)

                if b"Incorrect" not in a.stdout:
                    return b''.join(guess)

                perf_lines = a.stderr.split(b'\n')

                instr_count = None
                for i in perf_lines:
                    i = i.strip()
                    if b"instructions:u" in i:
                        instr_count = int(i.split()[0].replace(b',', b''))

                assert instr_count is not None, "Failed to find instr count"
                if instr_count > maxnum:
                    maxnum = instr_count
                    maxchar = gc
            guess_base.append(maxchar)
        print(f"Answer not found. Trying again... {guess=}")
    assert False, f"Could not find answer in {max_tries} tries :("


r = remote(HOST, int(PORT))

for round_num in range(20):
    r.readuntil(b"Crackme: ")

    bin_contents = b64decode(r.readline().strip())

    with open('chal_bin', 'wb') as f:
        f.write(bin_contents)
    print('solving', round_num+1)
    answer = solve_bin()

    r.sendlineafter(b"Password: ", answer)

r.interactive()
