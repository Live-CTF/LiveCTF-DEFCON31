#!/usr/bin/env python3

from pwn import *

do_it_live = True

if do_it_live:
  HOST = os.environ.get('HOST', 'localhost')
  PORT = 31337
  context.arch = 'amd64'
  io = remote(HOST, int(PORT))
else:
  env = {"FLAG":"LiveCTF{fakeflag}"}
  io = process('cd handout; python3 server.py', shell=True, env=env)


def solve(s : bytes):
  key_magic = bytes.fromhex("e61f4400c00286")
  addr = s.find(key_magic) + len(key_magic)
  key_offset = u32(s[addr:addr+4]) - 0x200000
  key = s[key_offset:key_offset+0x20]
  print(hex(key_offset))

  data_magic = bytes.fromhex("baff000000")
  addr = s.find(data_magic) - 4
  data_offset = u32(s[addr:addr+4]) - 0x200000
  data = bytearray(s[data_offset:data_offset+0x100])
  print(hex(data_offset))
  S = []
  for i in range(256):
    S.append(i)
  j = 0
  for i in range(256):
    j = (j + S[i] + key[i % 0x20]) % 256
    S[i], S[j] = S[j], S[i]

  n = 0
  for i in range(255):
    n = (n + 1) % 0x100
    tmp = S[n]
    j = (j + tmp) % 0x100
    S[n] = S[j]
    S[j] = tmp
    data[i] ^= S[(tmp + S[n]) % 0x100]

  s = disasm(data)

  passw = bytes([int(i, 16) for i in re.findall('cmp    BYTE PTR.*, 0x([0-9a-f]+)', s)])
  return passw

for round in range(20):
  io.recvuntil("Crackme: ")
  data = b64d(io.recvline().decode())
  passw = solve(data)
  io.sendlineafter("Password: ", passw)

io.recvuntil("flag: ")
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
io.close()
