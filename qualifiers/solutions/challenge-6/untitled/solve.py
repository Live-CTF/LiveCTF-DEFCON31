from pwn import *
import base64
import os

#r = remote("127.0.0.1",1235)
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
r = remote(HOST, int(PORT))

context.arch = 'amd64'

for i in range(20):
    r.recvuntil('Crackme: ')
    data = base64.b64decode(r.recvline())
    fval = b"\x00\xFF\xD0\x48\x8D\x9C\x24\x90\x00\x00\x00\x48\x8D\x74"
    offset = data.find(fval) + 1
    print(offset)

    shellcode = shellcraft.write(1, 'rax', 0x130)
    shellcode += shellcraft.exit(0)
    shellcode = asm(shellcode)
    payload = data[:offset] + shellcode + data[offset + len(shellcode):]

    with open("sample_ex.elf", "wb") as f:
        f.write(payload)

    os.system("chmod +x sample_ex.elf")

    p = process("sample_ex.elf")
    p.sendline("A")
    leak = p.recv()

    rs = []
    for l in disasm(leak).split('\n'):
        if 'cmp' in l:
            rs.append(int(l.split(',')[-1], 16))

    res = (''.join([chr(x) for x in rs]))

    p.close()
    r.sendlineafter(': ', res)


r.recvuntil("Congratulations! Here is the flag: ")
flag = r.recvline_contains(b'{').decode().strip()
log.info('Flag: %s', flag)
