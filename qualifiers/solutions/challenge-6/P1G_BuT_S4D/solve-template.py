#!/usr/bin/env python3

from pwn import *
import base64
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
# io = process("../handout/")
def RC4(key, cipher):
        S = [i for i in range(256)]

        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]

        i = 0
        plain = []
        for c in cipher:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]

            k = c ^ S[(S[i] + S[j]) % 256]
            plain.append(k)

        return bytes(plain)

for i in range(20):
    io.readuntil("Crackme: ")
    elf = io.readuntil("\nPassword:", drop = True)
    elf_buf = base64.b64decode(elf)
    cipher_offset = 0x000000000200348 - 0x000000000200000
    cipher = elf_buf[cipher_offset:cipher_offset + 256]
    
    magic_number = [0x48, 0x81, 0xF9, 0x00, 0x01, 0x00, 0x00, 0x74, 0x28, 0x44, 0x8A, 0x44, 0x0C, 0x80, 0x89, 0xCE, 0x83, 0xE6, 0x1F, 0x44, 0x00, 0xC0]
    magic_number = bytes(magic_number)
    
    data = elf_buf.split(magic_number)
    data = data[1][2:6]

    key_offset = u32(data) - 0x000000000200000
    key = elf_buf[key_offset: key_offset + 32]
    
    # print(f"[+] cipher : {cipher}")
    # print(f"[+] key: {key}")
    shellcode = RC4(key = key, cipher=cipher)
    # print(f"[+] shellcode: {shellcode}")
    # print(shellcode)

    lines = disasm(shellcode).split("\n")
    f = []
    for line in lines:
        if "cmp" in line:
            num = line.split(", ")[1]
            f.append(int(num, 16))
    print(bytes(f))
    io.sendline(bytes(f[1:]))

io.recvuntil("Congratulations! Here is the flag: ")
log.success(io.recvall().strip())
# io.interactive()
