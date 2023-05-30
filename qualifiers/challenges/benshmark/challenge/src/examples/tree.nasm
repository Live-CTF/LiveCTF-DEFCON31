[BITS 64]
push 0x2a
mov rbx, rsp

push 0xa
mov r14, rsp

pop r10
pop r10

mov r10, 1
mov r13, 30 

xor rax, rax
inc rax
mov rdi, rax
mov rdx, rax

drawrow:
xor r12, r12

drawrow_inner:
mov rsi, rbx
syscall
inc r12
cmp r12, r10
jl drawrow_inner

mov rsi, r14
syscall

inc r10
cmp r10, r13
jle drawrow

ret
