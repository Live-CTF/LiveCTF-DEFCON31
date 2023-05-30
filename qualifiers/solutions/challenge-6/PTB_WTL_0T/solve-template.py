#!/usr/bin/env python3

from pwn import *
import base64
import re

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
io = remote(HOST, int(PORT))
for i in range(20):
    io.recvuntil("Crackme: ")
    base64data = io.recvuntil(b"Password: ").strip(b"Password: ")
    decoded_data = base64.b64decode(base64data)

    with open(f"a{i}", "wb") as file:
        file.write(decoded_data)

    exe = ELF(f"./a{i}")
    context.arch = "amd64"
    key_addr = next(exe.search(asm("add al, r8b"))) + 3
    key_addr = u64(
        decoded_data[key_addr - 0x201000 + 2 : key_addr - 0x201000 + 2 + 4].ljust(
            8, b"\x00"
        )
    )

    key = exe.read(key_addr, 0x20)
    code = exe.read(0x200348, 0xFF)

    def rc4_crypto(buffer):
        box = list(range(256))
        outbuf = bytearray(buffer)
        j = 0
        for i in range(256):
            box[i] = i

        for _i in range(256):
            tmp = box[_i]
            j = (key[_i & 31] + tmp + j) & 0xFF
            box[_i] = box[j]
            box[j] = tmp

        __i = 0
        a = 0
        while __i != 255:
            a = (a + 1) & 0xFF
            _tmp = box[a]
            j = (_tmp + j) & 0xFF
            box[a] = box[j]
            box[j] = _tmp
            outbuf[__i] ^= box[(box[a] + _tmp) & 0xFF]
            __i += 1
        return bytes(outbuf)

    pt = rc4_crypto(code)
    instructions = pt.hex()
    input_text = disasm(bytes.fromhex(instructions))
    pattern = r"\s+cmp\s+(?:BYTE|QWORD) PTR \[rax(?:\+(?:0x[0-9a-fA-F]+)?)?\], (0x[0-9a-fA-F]+)"

    matches = re.findall(pattern, input_text)
    hex_codes = [match.strip() for match in matches]
    passcode = "".join(chr(int(hex_code, 16)) for hex_code in hex_codes)

    io.sendline(passcode)

flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
