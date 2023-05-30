#!/usr/bin/env python3

import os
import pwn
import subprocess
import re
import time
import tempfile
import base64
import glob

pwn.context.log_level = "CRITICAL" # supress connection log


def get_call_rax_address(elf_path):
    # "20246b:    ff d0                    callq  *%rax"
    out = subprocess.run(["objdump", "-d", elf_path], capture_output=True, text=True).stdout
    # print(out)
    match = re.search(r"(\w+):\s+ff \w{2}\s+callq?\s+\*%rax", out)
    assert match
    return int(match.group(1), 16)

# return input for "Correct"
def solve_one_crackme(elf_path) -> bytes:
    addr_call_rax = get_call_rax_address(elf_path)
    # print(f"{hex(addr_call_rax) = }")
    with pwn.process(["gdb", "--nx", elf_path]) as io:
        PROMPT = b"(gdb)"
        io.sendlineafter(PROMPT, b"set disable-randomization off") # Avoid "warning: Error disabling address space randomization: Operation not permitted"
        io.sendlineafter(PROMPT, b"set style enabled off") # disable coloring
        io.sendlineafter(PROMPT, b"set disassembly-flavor intel")
        io.sendlineafter(PROMPT, f"break *{hex(addr_call_rax)}".encode())
        io.sendlineafter(PROMPT, b"run")
        io.recvuntil(b"Starting program")
        time.sleep(0.5)
        io.sendline(b"DUMMY_INPUT")
        io.sendlineafter(PROMPT, b"si")
        io.sendlineafter(PROMPT, b"x/100i $rip")
        for _ in range(20):
            io.sendline(b"") # empty line will be nessesary for processing "Type <RET> for more, q to quit, c to continue without paging" line
        io.sendline(b"quit") # "exit" command does not exist!

        result = bytearray(64)
        for line in io.recvall().decode().split("\n"):
            # index 0
            # eg: "0x7ffff7ff700e:      cmp    BYTE PTR [rax],0x33"
            m = re.search(r"\w+:\s+cmp\s+BYTE PTR \[rax\],(\w+)", line)
            if m:
                result[0] = int(m.group(1), 0)
            else:
                # other index
                # eg: "0x7ffff7ff70f3:      cmp    BYTE PTR [rax+0x1f],0x31"
                m = re.search(r"\w+:\s+cmp\s+BYTE PTR \[rax\+(\w+)\],(\w+)", line)
                if m:
                    index = int(m.group(1), 0)
                    value = int(m.group(2), 0)
                    result[index] = value
    return bytes(result.rstrip(b"\x00"))

def solve_challenge(io):
    for i in range(20):
        io.recvuntil(b"Crackme: ")
        elf = base64.b64decode(io.recvline().decode())

        filename = f"challange_{i:02}.elf"
        with open(filename, "wb") as f:
            f.write(elf)
        subprocess.run(["chmod", "777", filename], capture_output=True, text=True)
        cracked_flag = solve_one_crackme(filename)
        io.sendlineafter(b"Password:", cracked_flag)
    print(io.recvall().decode())


HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

with pwn.remote(HOST, int(PORT)) as io: solve_challenge(io)
# with pwn.process(["python3", "../handout/server.py"], env={"FLAG":"flag{test}", "LOCAL":"1"}) as io: solve_challenge(io)

def test_local_samples():
    for f in glob.glob("../handout/samples/*.elf"):
        print(f)
        cracked_flag = solve_one_crackme(f)
        print(cracked_flag.decode())
