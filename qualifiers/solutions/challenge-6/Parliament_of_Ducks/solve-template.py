#!/usr/bin/env python3


from pwn import *
import base64
from time import sleep
import os, re

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

r = remote(HOST, int(PORT))

context.arch = 'amd64'
context.log_level = 'error'

NUM_ROUNDS = 20
for i in range(NUM_ROUNDS):
    r.recvuntil('Crackme: ')
    binary = base64.b64decode(r.recvline(keepends=False))
    with open(f'bin_{i}.elf', 'wb') as f:
        f.write(binary)
        f.flush()

    os.system(f"chmod +x bin_{i}.elf")

    pbin = ELF(f'bin_{i}.elf')
    call_pos = next(pbin.search(asm('call rax')))

    p = process(f'bin_{i}.elf')
    p.writemem(call_pos, asm("""
        mov rbx, 0x205555
        mov qword ptr [rbx], rax
        .L1:
        jmp .L1
    """))
    
    p.sendline(b'A'*0x20)
    sleep(0.5)
    func = u64(p.readmem(0x205555, 8))
    print(hex(func))
    
    res = disasm(p.readmem(func, 0x1000))
    ans = bytes(map(lambda x: int(x, 16), re.findall(r'cmp\s+BYTE PTR.*(0x\d{2})', res)))
    r.sendlineafter('Password: ', ans)

r.recvuntil('Here is the flag: ')

flag = r.recvline_contains(b'LiveCTF{').decode().strip()
print('Flag: %s', flag)

'''
# from Crypto.Cipher import ARC4

def key_scheduling(key):
    sched = [i for i in range(0, 256)]
    
    i = 0
    for j in range(0, 256):
        i = (i + sched[j] + key[j % len(key)]) % 256
        
        tmp = sched[j]
        sched[j] = sched[i]
        sched[i] = tmp
        
    return i, sched
    

def stream_generation(x, sched):
    stream = []
    i = 0
    j = x
    while True:
        i = (1 + i) % 256
        j = (sched[i] + j) % 256
        
        tmp = sched[j]
        sched[j] = sched[i]
        sched[i] = tmp
        
        yield sched[(sched[i] + sched[j]) % 256]        


from pwn import *
from base64 import b64decode

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
r = remote(HOST, int(PORT))


for i in range(20):
    r.recvuntil('Crackme: ')
    binary = b64decode(r.recvline())

    # binary = open("./samples/2fafe278392358d1e09a93673a889b16.elf", "rb").read()

    idx = u16(binary[0x1764:0x1764+2])
    key = binary[idx:idx+0x20]
    ct = binary[0x348:0x348+0xff]

    # key = b'0\xb2\xd4\xf9\x0bBp\xbf:\xc0\xbb\xb1\xdaA\xc6\x96\x9bm:\xffL\xfb\xcf\xf7Y9k\x12 \xda\x0e\x06'
    # ct = b'\x11\xc2\xbc~?V\xe1\x85\xd8\xb5<\x88h\x0b\x12Xm\x82\x80\x0e\x8b\x85\xff\xb0\xf7\x85\x07\xfa\xfc\x07\x90\xd1\xc1\x14E\x92\xb9\x81\xe7o\xa0\xe5Y2\xc8 \xf9\x1aov\xa1\xe6|\xcew(\x91#\xd2\xa5w\xba8\x1c\x12\xcbG|\x82T\x1a\xe4Y\x9a\x0c\xff\xf4s\x12\xbb\xf0wG\n\xa9d\xff\x9f8W\x8a\xdc\xe8\xe9\xbe\x969\xda\x16\x8f\x0f!\x8a\x98V3|\x81\xc3N9\xf9\x03}j\xaf\xed\xf5K\x04)\xa40\xfbA=\xbf\xc1#\x82\xbd\xb2\xaay(\xa1\x81\xc3\x94\x01O!\xd2Y\x9f\x0c\x0c=\x9ac\xd66\x89R\x10\x83s\x9dS\xcen \\8\xc57\x9c*\xebl\x82\x13\xeb\xc2}b\x9a+FJ\'(\xac\x15\x84\x10\xa6\x0c\xf2(\xf0\xa2\xaaB\xc61\x0fj\x19x5\xa7:\xe1<\xa6\xe2\x86Y7\x13\xe2\x99\xa4\x8a\xe1\x80\xc4\xebn\xe4\xb4\xac\xe8D\xbaa\xafw\xde\x90HY\xc23\x08\xa7\xc88\x16\x96#\xc7"\xa8\xdd\xb3\x13\xe6\xe3\x8eD\xffF\x08'

    x, sched = key_scheduling(key)
    key_stream = stream_generation(x, sched)

    pt = [c ^ next(key_stream) for c in ct]

    context.arch = "amd64"
    res = (disasm(bytes(pt)))

    a = res.split("cmp    BYTE PTR [")
    b = [_.split('],')[1].split('\n')[0] for _ in a[1:]]
    c = [int(_, 16) for _ in b]
    answer = bytes(c)
    # print(c)
    r.sendlineafter('Password: ', answer)

r.recvuntil('Here is the flag: ')

flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
'''
