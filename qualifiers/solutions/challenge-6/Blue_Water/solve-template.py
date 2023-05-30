#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
# context.log_level = 'debug'

r = remote(HOST, int(PORT))

class TwistedRC4:
    def __init__(self, key: bytes):
        assert len(key) == 32
        self.S = list(range(256))
        self.j = 0
        for i in range(256):
            self.j = (key[i%len(key)] + self.S[i] + self.j) % 256
            self.S[i], self.S[self.j] = self.S[self.j], self.S[i]
    def gao(self, data: bytes):
        data = bytearray(data)
        i = 0
        for pos in range(255):
            i = i + 1
            self.j = (self.S[i] + self.j) % 256
            self.S[i], self.S[self.j] = self.S[self.j], self.S[i]
            data[pos] ^= self.S[(self.S[i] + self.S[self.j]) % 256]
        return bytes(data)
 

def solve(path):
    bi = ELF(path)
    fuck = read(path)
    pos = fuck.find(bytes.fromhex("4400C00286"))
    # key_addr = bi.u32(0x202764)
    key_addr = u32(fuck[pos+5:pos+9])
    rc4_key = bi.read(key_addr, 32)
    pos = fuck.find(bytes.fromhex("48 8D 9C 24 C8 01 00 00"))
    code_addr = u32(fuck[pos+9:pos+13])
    code = bi.read(0x200348, 255)
    code = TwistedRC4(rc4_key).gao(code)
    off = code.find(b"\x80\x38")
    ans = [None] * 32
    ans[0] = (code[off+2])
    for i in range(1, 0x20):
        off = code.find(b"\x80\x78", off+1)
        ans[code[off+2]] = code[off+3]
    return bytes(ans)

for i in range(20):
    r.recvuntil(b"Crackme: ")
    data = r.recvline().strip()
    data = base64.b64decode(data)
    with open("/tmp/crackme", "wb") as f:
        f.write(data)
    ans = solve("/tmp/crackme")
    print("ans", ans)
    r.sendlineafter(b"Password: ", ans)

print(r.recvall())
