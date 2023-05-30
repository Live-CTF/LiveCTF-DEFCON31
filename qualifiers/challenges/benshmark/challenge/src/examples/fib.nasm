[BITS 64]
mov rbx, 0
mov rcx, 1
mov rdx, 1
mov r12, 0
mov r13, 90
fibonacci:
mov r12, rcx
add r12, rbx
mov rbx, rcx
mov rcx, r12
dec r13
cmp r13, 0
jg fibonacci
mov rax, 60
xor rdi, rdi
syscall
