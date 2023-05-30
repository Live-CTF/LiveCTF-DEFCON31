#!/usr/bin/env python3
from pwn import *
import base64
import os
context.arch="amd64"
#context.log_level='debug'
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
io = remote(HOST, int(PORT))
#io = process(["python3","server.py"],env={"FLAG":"testflag","LOCAL":"1"})
for i in range(20):
    io.recvuntil("Crackme:")
    binary=io.recvline().decode("utf-8").strip()
    binary=base64.b64decode(binary)
    with open("elf","wb") as f:
        f.write(binary)
    #f="./samples/1bcb8edab8fb41de17ce26420acbf3a5.elf"
    os.system("chmod +x ./elf")
    f="elf"
    e=ELF(f)
    call_rax=next(e.search(asm("call rax")))
    print(hex(call_rax))
    p=process(["gdb",f])
    p.sendline(f"b *{hex(call_rax)}\nr\n")
    sleep(0.5)
    p.sendline(f"dump memory testfile $rax ($rax+0x200)\n")
    sleep(0.5)
    p.close()
    ans=""
    with open("testfile","rb") as f:
        dis=disasm(f.read())
        #print(dis)
        fi="cmp    BYTE PTR [rax], "
        idx=dis.find(fi)+len(fi)
        en=dis[idx:].find("\n")
        ans+=chr(int(dis[idx+2:idx+en],16))
        for i in range(0x1f):
            fi=f"cmp    BYTE PTR [rax+{hex(i+1)}], "
            idx=dis.find(fi)+len(fi)
            en=dis[idx:].find("\n")
            ans+=chr(int(dis[idx+2:idx+en],16))

    io.sendlineafter("Password:",ans)
io.recvuntil("Congratulations! Here is the flag:")
flag=io.recvline()
print(flag)
io.interactive()

