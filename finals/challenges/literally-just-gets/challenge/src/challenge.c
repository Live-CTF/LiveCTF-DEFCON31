#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h>

// Yes, I copied this from ioctl-me-maybe :)
__attribute__((naked)) void all_the_gadgets()
{
    __asm__(
        "jmp %rsp\nret\n"
        "pop %rax\nret\n"
        "pop %rbx\nret\n"
        "pop %rcx\nret\n"
        "pop %rdx\nret\n"
        "pop %rsi\nret\n"
        "pop %rdi\nret\n"
        "pop %rsp\nret\n"
        "pop %rbp\nret\n"
        "pop %r8\nret\n"
        "pop %r9\nret\n"
        "pop %r10\nret\n"
        "pop %r11\nret\n"
        "pop %r12\nret\n"
        "pop %r13\nret\n"
        "pop %r14\nret\n"
        "pop %r15\nret\n"
        "mov %rax, %rax\nret\n"
        "mov %rax, %rbx\nret\n"
        "mov %rax, %rcx\nret\n"
        "mov %rax, %rdx\nret\n"
        "mov %rax, %rsi\nret\n"
        "mov %rax, %rdi\nret\n"
        "mov %rax, %rsp\nret\n"
        "mov %rax, %rbp\nret\n"
        "mov %rax, %r8\nret\n"
        "mov %rax, %r9\nret\n"
        "mov %rax, %r10\nret\n"
        "mov %rax, %r11\nret\n"
        "mov %rax, %r12\nret\n"
        "mov %rax, %r13\nret\n"
        "mov %rax, %r14\nret\n"
        "mov %rax, %r15\nret\n"
        "mov %rax, %rax\nret\n"
        "mov %rbx, %rax\nret\n"
        "mov %rcx, %rax\nret\n"
        "mov %rdx, %rax\nret\n"
        "mov %rsi, %rax\nret\n"
        "mov %rdi, %rax\nret\n"
        "mov %rsp, %rax\nret\n"
        "mov %rbp, %rax\nret\n"
        "mov %r8, %rax\nret\n"
        "mov %r9, %rax\nret\n"
        "mov %r10, %rax\nret\n"
        "mov %r11, %rax\nret\n"
        "mov %r12, %rax\nret\n"
        "mov %r13, %rax\nret\n"
        "mov %r14, %rax\nret\n"
        "mov %r15, %rax\nret\n"
        "mov 0(%rax), %rcx\nret\n"
        "mov %rcx, 0(%rax)\nret\n"
        "syscall\nret\n"
    );
}

void init(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
}

int main(int argc, char** argv, char** envp)
{
    init();

    printf("SUDDEN DEATH !! IT'S JUST GETS()\n");

    char buf[0x100];
    gets(buf);

    return 0;
}
